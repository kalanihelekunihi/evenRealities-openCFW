# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/shared/liblc3"
PROVIDER_C = COMPONENT / "runtime_liblc3_encoder_provider.c"
PROVIDER_H = COMPONENT / "runtime_liblc3_encoder_provider.h"
ADMISSION = COMPONENT / "encoder_source_admission.json"
TARGET_COMPAT = COMPONENT / "target_compat"
UPSTREAM = ROOT / "third_party/liblc3"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
ENCODER_SOURCE_NAMES = (
    "attdet", "bits", "bwdet", "energy", "lc3", "ltpf", "mdct", "sns",
    "spec", "tables", "tns",
)
ENCODER_SOURCES = tuple(UPSTREAM_SRC / f"{name}.c"
                        for name in ENCODER_SOURCE_NAMES)
HOST_SOURCES = ENCODER_SOURCES + (UPSTREAM_SRC / "plc.c",)


class Config(ctypes.Structure):
    _fields_ = [
        ("frame_us", ctypes.c_uint32),
        ("sample_rate_hz", ctypes.c_uint32),
        ("pcm_sample_rate_hz", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
        ("pcm_format", ctypes.c_uint32),
        ("pcm_stride", ctypes.c_uint32),
    ]


class Plan(ctypes.Structure):
    _fields_ = [
        ("encoded_samples_per_frame", ctypes.c_uint32),
        ("pcm_samples_per_frame", ctypes.c_uint32),
        ("frame_bytes", ctypes.c_uint32),
        ("encoder_bytes", ctypes.c_uint32),
        ("pcm_frame_bytes", ctypes.c_uint32),
        ("pcm_sample_bytes", ctypes.c_uint32),
        ("storage_alignment", ctypes.c_uint32),
    ]


class Provider(ctypes.Structure):
    _fields_ = [
        ("initialized_seal", ctypes.c_uint32),
        ("encoder", ctypes.c_void_p),
        ("storage_size", ctypes.c_uint32),
        ("config", Config),
        ("plan", Plan),
    ]


class RuntimeLiblc3EncoderProviderTests(unittest.TestCase):
    OK = 0
    INVALID = -1
    STORAGE_TOO_SMALL = -2
    PCM_TOO_SHORT = -3
    OUTPUT_TOO_SMALL = -4
    MISALIGNED = -5
    OVERLAP = -6
    NOT_INITIALIZED = -8

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        cls.nm = shutil.which("nm")
        cls.lld = shutil.which("ld.lld")
        if cls.clang is None or cls.nm is None:
            raise unittest.SkipTest("Clang and nm are required")
        cls.tmp = tempfile.TemporaryDirectory(prefix="opencfw-liblc3-encoder-")
        library = Path(cls.tmp.name) / (
            "encoder-provider.dylib" if sys.platform == "darwin"
            else "encoder-provider.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-ffast-math", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-I", str(UPSTREAM_INCLUDE),
            "-I", str(UPSTREAM_SRC), "-I", str(COMPONENT), str(PROVIDER_C),
            *(str(path) for path in HOST_SOURCES),
        ]
        command += (["-dynamiclib", "-o", str(library)]
                    if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-lm", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))

        cls.plan_call = cls.lib.open_cfw_liblc3_encoder_provider_plan
        cls.plan_call.argtypes = [ctypes.POINTER(Config), ctypes.POINTER(Plan)]
        cls.plan_call.restype = ctypes.c_int
        cls.setup = cls.lib.open_cfw_liblc3_encoder_provider_setup
        cls.setup.argtypes = [ctypes.POINTER(Provider), ctypes.POINTER(Config),
                              ctypes.c_void_p, ctypes.c_size_t]
        cls.setup.restype = ctypes.c_int
        cls.encode = cls.lib.open_cfw_liblc3_encoder_provider_encode
        cls.encode.argtypes = [ctypes.POINTER(Provider), ctypes.c_void_p,
                               ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
        cls.encode.restype = ctypes.c_int
        cls.close = cls.lib.open_cfw_liblc3_encoder_provider_close
        cls.close.argtypes = [ctypes.POINTER(Provider)]

        cls.direct_setup = cls.lib.lc3_setup_encoder
        cls.direct_setup.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_void_p]
        cls.direct_setup.restype = ctypes.c_void_p
        cls.direct_encode = cls.lib.lc3_encode
        cls.direct_encode.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                      ctypes.c_void_p, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_void_p]
        cls.direct_encode.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def config(**overrides: int) -> Config:
        values = {
            "frame_us": 10_000,
            "sample_rate_hz": 16_000,
            "pcm_sample_rate_hz": 0,
            "bitrate_bps": 32_000,
            "pcm_format": 0,
            "pcm_stride": 1,
        }
        values.update(overrides)
        return Config(**values)

    def make_plan(self, config: Config) -> Plan:
        plan = Plan()
        self.assertEqual(self.plan_call(ctypes.byref(config), ctypes.byref(plan)), 0)
        return plan

    @staticmethod
    def storage(size: int) -> ctypes.Array[ctypes.c_uint64]:
        return (ctypes.c_uint64 * ((size + 7) // 8))()

    def test_fixed_abi_and_complete_non_hr_geometry(self) -> None:
        self.assertEqual(ctypes.sizeof(Config), 24)
        self.assertEqual(ctypes.sizeof(Plan), 28)
        for duration_us in (2_500, 5_000, 7_500, 10_000):
            for sample_rate_hz in (8_000, 16_000, 24_000, 32_000, 48_000):
                for pcm_format, width in enumerate((2, 4, 3, 4)):
                    with self.subTest(duration=duration_us,
                                      rate=sample_rate_hz, fmt=pcm_format):
                        config = self.config(frame_us=duration_us,
                            sample_rate_hz=sample_rate_hz,
                            pcm_format=pcm_format, pcm_stride=2)
                        plan = self.make_plan(config)
                        samples = duration_us * sample_rate_hz // 1_000_000
                        self.assertEqual(plan.encoded_samples_per_frame, samples)
                        self.assertEqual(plan.pcm_samples_per_frame, samples)
                        self.assertEqual(plan.pcm_sample_bytes, width)
                        self.assertEqual(plan.pcm_frame_bytes,
                            ((samples - 1) * 2 + 1) * width)
                        self.assertEqual(plan.storage_alignment, 8)

    def test_invalid_config_does_not_publish_a_partial_plan(self) -> None:
        invalid = (
            self.config(frame_us=6_000),
            self.config(sample_rate_hz=44_100),
            self.config(sample_rate_hz=48_000, pcm_sample_rate_hz=16_000),
            self.config(pcm_format=4),
            self.config(pcm_stride=0),
            self.config(pcm_stride=0x80000000),
            self.config(bitrate_bps=0x80000000),
        )
        for config in invalid:
            values = tuple(getattr(config, name) for name, _ in Config._fields_)
            with self.subTest(config=values):
                plan = Plan(*(0xA5A5A5A5 for _ in range(7)))
                self.assertEqual(self.plan_call(ctypes.byref(config),
                                                ctypes.byref(plan)), self.INVALID)
                self.assertEqual(
                    tuple(getattr(plan, name) for name, _ in Plan._fields_),
                    (0xA5A5A5A5,) * 7)

    def test_setup_alignment_size_overlap_and_close(self) -> None:
        config = self.config()
        plan = self.make_plan(config)
        storage = self.storage(plan.encoder_bytes)
        provider = Provider()
        self.assertEqual(self.setup(ctypes.byref(provider), ctypes.byref(config),
            storage, plan.encoder_bytes - 1), self.STORAGE_TOO_SMALL)
        self.assertFalse(provider.encoder)
        self.assertEqual(self.setup(ctypes.byref(provider), ctypes.byref(config),
            ctypes.c_void_p(ctypes.addressof(storage) + 1),
            plan.encoder_bytes), self.MISALIGNED)
        self.assertEqual(self.setup(ctypes.byref(provider), ctypes.byref(config),
            ctypes.byref(provider), plan.encoder_bytes), self.OVERLAP)
        self.assertEqual(self.setup(ctypes.byref(provider), ctypes.byref(config),
            storage, ctypes.sizeof(storage)), self.OK)
        self.assertNotEqual(provider.initialized_seal, 0)
        self.assertEqual(provider.encoder, ctypes.addressof(storage))
        self.assertEqual(provider.config.pcm_sample_rate_hz,
                         config.sample_rate_hz)
        self.close(ctypes.byref(provider))
        self.assertEqual((provider.initialized_seal, provider.encoder,
                          provider.storage_size), (0, None, 0))

    @staticmethod
    def pcm_for(fmt: int, samples: int, stride: int):
        scalar_span = (samples - 1) * stride + 1
        values = [((index * 997) % 20_001) - 10_000
                  for index in range(samples)]
        if fmt == 0:
            pcm = (ctypes.c_int16 * scalar_span)()
            for index, value in enumerate(values):
                pcm[index * stride] = value
        elif fmt == 1:
            pcm = (ctypes.c_int32 * scalar_span)()
            for index, value in enumerate(values):
                pcm[index * stride] = value << 8
        elif fmt == 2:
            pcm = (ctypes.c_uint8 * (3 * scalar_span))()
            for index, value in enumerate(values):
                packed = (value << 8) & 0xFFFFFF
                offset = 3 * index * stride
                pcm[offset:offset + 3] = (
                    packed & 0xFF, (packed >> 8) & 0xFF,
                    (packed >> 16) & 0xFF)
        else:
            pcm = (ctypes.c_float * scalar_span)()
            for index, value in enumerate(values):
                pcm[index * stride] = value / 10_000.0
        return pcm

    def test_all_pcm_formats_match_pristine_upstream_with_byte_bounds(self) -> None:
        for pcm_format in range(4):
            with self.subTest(pcm_format=pcm_format):
                config = self.config(pcm_format=pcm_format, pcm_stride=2,
                                     pcm_sample_rate_hz=48_000)
                plan = self.make_plan(config)
                wrapped_storage = self.storage(plan.encoder_bytes)
                direct_storage = self.storage(plan.encoder_bytes)
                provider = Provider()
                self.assertEqual(self.setup(ctypes.byref(provider),
                    ctypes.byref(config), wrapped_storage,
                    ctypes.sizeof(wrapped_storage)), self.OK)
                direct = self.direct_setup(config.frame_us,
                    config.sample_rate_hz, config.pcm_sample_rate_hz,
                    direct_storage)
                self.assertEqual(direct, ctypes.addressof(direct_storage))
                pcm = self.pcm_for(pcm_format, plan.pcm_samples_per_frame,
                                   config.pcm_stride)
                self.assertEqual(ctypes.sizeof(pcm), plan.pcm_frame_bytes)
                wrapped_output = (ctypes.c_uint8 * plan.frame_bytes)()
                direct_output = (ctypes.c_uint8 * plan.frame_bytes)()
                self.assertEqual(self.encode(ctypes.byref(provider), pcm,
                    plan.pcm_frame_bytes - 1, wrapped_output,
                    plan.frame_bytes), self.PCM_TOO_SHORT)
                self.assertEqual(self.encode(ctypes.byref(provider), pcm,
                    plan.pcm_frame_bytes, wrapped_output,
                    plan.frame_bytes - 1), self.OUTPUT_TOO_SMALL)
                self.assertEqual(self.encode(ctypes.byref(provider), pcm,
                    plan.pcm_frame_bytes, wrapped_output,
                    plan.frame_bytes), self.OK)
                self.assertEqual(self.direct_encode(direct, pcm_format, pcm,
                    config.pcm_stride, plan.frame_bytes, direct_output), 0)
                self.assertEqual(bytes(wrapped_output), bytes(direct_output))
                self.assertNotEqual(bytes(wrapped_output), bytes(plan.frame_bytes))

    def test_state_tampering_and_storage_alias_fail_before_upstream(self) -> None:
        # S24 and float have the same width and therefore the same plan.  A
        # format mutation between them specifically exercises the seal rather
        # than being caught by plan re-derivation alone.
        config = self.config(pcm_format=1)
        plan = self.make_plan(config)
        storage = self.storage(plan.encoder_bytes)
        provider = Provider()
        output = (ctypes.c_uint8 * plan.frame_bytes)()
        pcm = self.pcm_for(1, plan.pcm_samples_per_frame, 1)
        self.assertEqual(self.setup(ctypes.byref(provider), ctypes.byref(config),
            storage, ctypes.sizeof(storage)), self.OK)
        self.assertEqual(self.encode(ctypes.byref(provider), storage,
            plan.pcm_frame_bytes, output, plan.frame_bytes), self.OVERLAP)
        self.assertEqual(self.encode(ctypes.byref(provider), pcm,
            plan.pcm_frame_bytes, storage, plan.frame_bytes), self.OVERLAP)
        raw = (ctypes.c_uint8 * (plan.pcm_frame_bytes + 1))()
        misaligned = ctypes.c_void_p(ctypes.addressof(raw) + 1)
        self.assertEqual(self.encode(ctypes.byref(provider), misaligned,
            plan.pcm_frame_bytes, output, plan.frame_bytes), self.MISALIGNED)
        provider.config.pcm_format = 3
        self.assertEqual(self.encode(ctypes.byref(provider), pcm,
            plan.pcm_frame_bytes, output, plan.frame_bytes), self.NOT_INITIALIZED)

    def test_cortex_m55_objects_symbols_relocations_and_budgets(self) -> None:
        admission = json.loads(ADMISSION.read_text())
        output_dir = Path(self.tmp.name) / "arm"
        output_dir.mkdir()
        sources = dict(zip(ENCODER_SOURCE_NAMES, ENCODER_SOURCES))
        sources["provider"] = PROVIDER_C
        objects: dict[str, Path] = {}
        target_flags = admission["target_profile"]
        for name, source in sources.items():
            output = output_dir / f"{name}.o"
            subprocess.run([self.clang, *target_flags,
                "-I", str(TARGET_COMPAT), "-I", str(UPSTREAM_INCLUDE),
                "-I", str(UPSTREAM_SRC), "-I", str(COMPONENT),
                "-c", str(source), "-o", str(output)], check=True,
                capture_output=True, text=True)
            self.assertLessEqual(output.stat().st_size,
                admission["object_size_budgets"][f"{name}.o"])
            objects[name] = output

        defined: set[str] = set()
        undefined: set[str] = set()
        provider_symbols = ""
        for name, obj in objects.items():
            symbols = subprocess.run([self.nm, str(obj)], check=True,
                capture_output=True, text=True).stdout
            defined.update(re.findall(r"^[0-9a-fA-F]+\s+[A-Za-z]\s+(\S+)$",
                                      symbols, re.M))
            undefined.update(re.findall(r"^\s+U\s+(\S+)$", symbols, re.M))
            if name == "provider":
                provider_symbols = symbols
        unresolved = undefined - defined
        discarded_only = set(
            admission["discarded_section_only_external_relocations"])
        self.assertEqual(unresolved,
            set(admission["allowed_external_runtime_relocations"]) |
            discarded_only)
        for entry in admission["provider_entries"]:
            self.assertRegex(provider_symbols, rf"\b{entry}\n")
        # Apple Clang emits canonical CANTUNWIND rows even with both unwind
        # flags disabled.  The admission contract permits a mini-linker to
        # discard only those reviewed rows, matching the existing LTPF route.
        self.assertIn(".ARM.exidx.text.open_cfw_liblc3_encoder_provider_plan",
            subprocess.run(
            ["objdump", "-h", str(objects["provider"])], check=True,
            capture_output=True, text=True).stdout)

        if self.lld is None:
            self.skipTest("ld.lld required for retained encoder closure audit")
        linked = output_dir / "encoder-retained.o"
        roots = admission["link_contract"]["roots"]
        subprocess.run([self.lld, "-m", "armelf", "-r", "--gc-sections",
            f"--entry={roots[2]}", *(f"--undefined={root}" for root in roots),
            "-o", str(linked), *(str(objects[name]) for name in sources)],
            check=True, capture_output=True, text=True)
        self.assertLessEqual(linked.stat().st_size,
            admission["link_contract"]["qualification_relocatable_object_budget"])
        retained_symbols = subprocess.run([self.nm, str(linked)], check=True,
            capture_output=True, text=True).stdout
        retained_undefined = set(re.findall(
            r"^\s+U\s+(\S+)$", retained_symbols, re.M))
        self.assertEqual(retained_undefined,
            set(admission["allowed_external_runtime_relocations"]))
        for discarded in discarded_only:
            self.assertNotRegex(retained_symbols, rf"\b{discarded}\b")

    def test_license_and_route_state_are_explicit(self) -> None:
        admission = json.loads(ADMISSION.read_text())
        self.assertEqual(admission["license"], "Apache-2.0")
        self.assertTrue(admission["production_capable_source"])
        self.assertFalse(admission["overlay_routed"])
        self.assertFalse(admission["exact_generating_checkout_proven"])
        self.assertIn("SPDX-License-Identifier: Apache-2.0",
                      PROVIDER_C.read_text())
        self.assertIn("SPDX-License-Identifier: Apache-2.0",
                      PROVIDER_H.read_text())


if __name__ == "__main__":
    unittest.main()
