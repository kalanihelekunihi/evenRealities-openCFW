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
PROVIDER_C = COMPONENT / "runtime_liblc3_ltpf_provider.c"
PROVIDER_H = COMPONENT / "runtime_liblc3_ltpf_provider.h"
ADMISSION = COMPONENT / "ltpf_source_admission.json"
TARGET_COMPAT = COMPONENT / "target_compat"
UPSTREAM = ROOT / "third_party/liblc3"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
UPSTREAM_SOURCES = tuple(UPSTREAM_SRC / name for name in (
    "attdet.c", "bits.c", "bwdet.c", "energy.c", "lc3.c", "ltpf.c",
    "mdct.c", "plc.c", "sns.c", "spec.c", "tables.c", "tns.c"))
TARGET_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffast-math",
    "-fshort-enums", "-ffreestanding", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror")


class Config(ctypes.Structure):
    _fields_ = [("duration_index", ctypes.c_uint8),
                ("sample_rate_index", ctypes.c_uint8),
                ("reserved", ctypes.c_uint8 * 2)]


class Plan(ctypes.Structure):
    _fields_ = [("frame_samples", ctypes.c_uint32),
                ("history_samples", ctypes.c_uint32),
                ("total_samples", ctypes.c_uint32),
                ("current_offset_bytes", ctypes.c_uint32)]


class State(ctypes.Structure):
    _fields_ = [("words", ctypes.c_uint64 * 145)]


class Result(ctypes.Structure):
    _fields_ = [("pitch_present", ctypes.c_uint8),
                ("active", ctypes.c_uint8),
                ("reserved", ctypes.c_uint8 * 2),
                ("pitch_index", ctypes.c_int32)]


class UpstreamData(ctypes.Structure):
    _fields_ = [("active", ctypes.c_bool), ("pitch_index", ctypes.c_int)]


class RuntimeLiblc3LtpfProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang required")
        cls.tmp = tempfile.TemporaryDirectory(prefix="opencfw-liblc3-ltpf-")
        library = Path(cls.tmp.name) / (
            "ltpf-provider.dylib" if sys.platform == "darwin" else "ltpf-provider.so")
        command = [cls.clang, "-std=c11", "-O2", "-ffast-math",
                   "-fshort-enums", "-Wall", "-Wextra", "-Werror",
                   "-I", str(UPSTREAM_INCLUDE), "-I", str(UPSTREAM_SRC),
                   "-I", str(COMPONENT), str(PROVIDER_C),
                   *(str(path) for path in UPSTREAM_SOURCES)]
        command += (["-dynamiclib", "-o", str(library)] if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-lm", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.plan = cls.lib.open_cfw_liblc3_ltpf_plan
        cls.plan.argtypes = [ctypes.POINTER(Config), ctypes.POINTER(Plan)]
        cls.plan.restype = ctypes.c_int
        cls.reset = cls.lib.open_cfw_liblc3_ltpf_reset
        cls.reset.argtypes = [ctypes.POINTER(State)]
        cls.analyse = cls.lib.open_cfw_liblc3_ltpf_analyse_bounded
        cls.analyse.argtypes = [ctypes.POINTER(State), ctypes.POINTER(Config),
            ctypes.POINTER(Plan), ctypes.POINTER(ctypes.c_int16), ctypes.c_size_t,
            ctypes.POINTER(Result)]
        cls.analyse.restype = ctypes.c_int
        cls.direct = cls.lib.lc3_ltpf_analyse
        cls.direct.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(State),
                               ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(UpstreamData)]
        cls.direct.restype = ctypes.c_bool

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_fixed_abi_and_all_frame_plans(self):
        self.assertEqual((ctypes.sizeof(Config), ctypes.sizeof(Plan),
                          ctypes.sizeof(State), ctypes.sizeof(Result)),
                         (4, 16, 1160, 8))
        rates = (8000, 16000, 24000, 32000, 48000, 48000, 96000)
        histories = (9, 19, 29, 39, 59, 59, 119)
        for dt, duration_us in enumerate((2500, 5000, 7500, 10000)):
            for sr, sample_rate_hz in enumerate(rates):
                config = Config(dt, sr, (ctypes.c_uint8 * 2)(0, 0))
                plan = Plan()
                self.assertEqual(self.plan(ctypes.byref(config), ctypes.byref(plan)), 0)
                frame = sample_rate_hz * duration_us // 1_000_000
                self.assertEqual((plan.frame_samples, plan.history_samples,
                                  plan.total_samples, plan.current_offset_bytes),
                                 (frame, histories[sr], frame + histories[sr],
                                  2 * histories[sr]))

    def test_bounded_provider_matches_upstream_for_all_dispatch_slots(self):
        for sr in range(7):
            config = Config(3, sr, (ctypes.c_uint8 * 2)(0, 0))
            plan = Plan()
            self.assertEqual(self.plan(ctypes.byref(config), ctypes.byref(plan)), 0)
            raw = (ctypes.c_int16 * (plan.total_samples + 1))()
            samples = ctypes.cast(ctypes.byref(raw, 2), ctypes.POINTER(ctypes.c_int16))
            for index in range(plan.total_samples):
                samples[index] = ((index * 811 + sr * 37) % 20001) - 10000
            wrapped, direct = State(), State()
            result, upstream = Result(), UpstreamData()
            self.reset(ctypes.byref(wrapped))
            self.assertEqual(self.analyse(ctypes.byref(wrapped), ctypes.byref(config),
                ctypes.byref(plan), samples, plan.total_samples, ctypes.byref(result)), 0)
            current = ctypes.cast(ctypes.byref(raw, 2 + 2 * plan.history_samples),
                                  ctypes.POINTER(ctypes.c_int16))
            present = self.direct(3, sr, ctypes.byref(direct), current,
                                  ctypes.byref(upstream))
            self.assertEqual((result.pitch_present, result.active, result.pitch_index),
                             (int(present), int(upstream.active), upstream.pitch_index))
            self.assertEqual(bytes(wrapped), bytes(direct))

    def test_input_bounds_alignment_and_forged_plan_fail_closed(self):
        config = Config(3, 1, (ctypes.c_uint8 * 2)(0, 0))
        plan, state, result = Plan(), State(), Result()
        self.assertEqual(self.plan(ctypes.byref(config), ctypes.byref(plan)), 0)
        raw = (ctypes.c_int16 * (plan.total_samples + 1))()
        aligned = ctypes.cast(ctypes.byref(raw, 2), ctypes.POINTER(ctypes.c_int16))
        self.assertEqual(self.analyse(ctypes.byref(state), ctypes.byref(config),
            ctypes.byref(plan), aligned, plan.total_samples - 1,
            ctypes.byref(result)), -2)
        misaligned = ctypes.cast(raw, ctypes.POINTER(ctypes.c_int16))
        self.assertEqual(self.analyse(ctypes.byref(state), ctypes.byref(config),
            ctypes.byref(plan), misaligned, plan.total_samples,
            ctypes.byref(result)), -3)
        plan.history_samples += 1
        self.assertEqual(self.analyse(ctypes.byref(state), ctypes.byref(config),
            ctypes.byref(plan), aligned, plan.total_samples,
            ctypes.byref(result)), -1)

    def test_cortex_m55_symbols_relocations_and_budgets(self):
        temporary = Path(self.tmp.name)
        objects = {}
        for source, name in ((UPSTREAM_SRC / "ltpf.c", "ltpf"),
                             (PROVIDER_C, "provider")):
            output = temporary / f"{name}.o"
            subprocess.run([self.clang, *TARGET_FLAGS, "-I", str(TARGET_COMPAT),
                "-I", str(UPSTREAM_INCLUDE), "-I", str(UPSTREAM_SRC),
                "-I", str(COMPONENT), "-c", str(source), "-o", str(output)],
                check=True, capture_output=True, text=True)
            objects[name] = output
        admission = json.loads(ADMISSION.read_text())
        self.assertLessEqual(objects["ltpf"].stat().st_size,
                             admission["object_size_budgets"]["ltpf_o"])
        self.assertLessEqual(objects["provider"].stat().st_size,
                             admission["object_size_budgets"]["provider_o"])
        symbols = subprocess.run(["objdump", "-t", str(objects["ltpf"])],
                                 check=True, capture_output=True, text=True).stdout
        for symbol in ("lc3_ltpf_analyse", "resample_8k_12k8",
                       "resample_16k_12k8", "resample_24k_12k8",
                       "resample_32k_12k8", "resample_48k_12k8",
                       "resample_96k_12k8"):
            self.assertRegex(symbols, rf"\b{symbol}\n")
        relocs = subprocess.run(["objdump", "-r", str(objects["ltpf"])],
                                check=True, capture_output=True, text=True).stdout
        section = relocs.split("RELOCATION RECORDS FOR [.text.lc3_ltpf_analyse]:", 1)[1].split("RELOCATION RECORDS FOR", 1)[0]
        externals = {value for value in re.findall(r"R_ARM_\S+\s+(\S+)", section)
                     if value in {"memmove", "sqrtf"}}
        self.assertEqual(externals, {"memmove", "sqrtf"})
        provider_relocs = subprocess.run(["objdump", "-r", str(objects["provider"])],
                                         check=True, capture_output=True, text=True).stdout
        self.assertIn("lc3_ltpf_analyse", provider_relocs)
        self.assertIn("memset", provider_relocs)

    def test_license_admission_and_historical_boundaries(self):
        admission = json.loads(ADMISSION.read_text())
        self.assertEqual(admission["license"], "Apache-2.0")
        self.assertTrue(admission["production_capable_source"])
        self.assertTrue(admission["source_provider_supports_all_dispatch_slots"])
        self.assertFalse(admission["individual_historical_body_routing"])
        self.assertTrue(admission["overlay_routed"])
        self.assertEqual(admission["allowed_external_relocations"]["production_overlay"], [])
        self.assertEqual(admission["reviewed_profiles"]["apple-clang"]["source_owned_bytes"], 7576)
        self.assertEqual(admission["reviewed_profiles"]["linux-clang"]["source_owned_bytes"], 7596)
        self.assertEqual(set(admission["historical_non_corpus_boundaries"]),
                         {"0x00438400", "0x00438604"})
        self.assertIn("SPDX-License-Identifier: Apache-2.0", PROVIDER_C.read_text())
        self.assertIn("SPDX-License-Identifier: Apache-2.0", PROVIDER_H.read_text())


if __name__ == "__main__":
    unittest.main()
