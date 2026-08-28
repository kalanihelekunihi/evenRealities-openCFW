from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "shared" / "liblc3"
SOURCE = COMPONENT / "runtime_liblc3_encoder_candidate.c"
HEADER = COMPONENT / "runtime_liblc3_encoder_candidate.h"
TARGET_COMPAT = COMPONENT / "target_compat"
UPSTREAM = ROOT / "third_party" / "liblc3"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
UPSTREAM_SOURCES = tuple(
    UPSTREAM_SRC / name
    for name in (
        "attdet.c",
        "bits.c",
        "bwdet.c",
        "energy.c",
        "lc3.c",
        "ltpf.c",
        "mdct.c",
        "plc.c",
        "sns.c",
        "spec.c",
        "tables.c",
        "tns.c",
    )
)

TARGET_FLAGS = (
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-mfloat-abi=hard",
    "-std=c11",
    "-O2",
    "-ffast-math",
    "-fshort-enums",
    "-ffreestanding",
    "-fno-builtin",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
)


class EncoderConfig(ctypes.Structure):
    _fields_ = [
        ("frame_us", ctypes.c_uint32),
        ("sample_rate_hz", ctypes.c_uint32),
        ("pcm_sample_rate_hz", ctypes.c_uint32),
        ("bitrate_bps", ctypes.c_uint32),
        ("pcm_format", ctypes.c_uint32),
        ("pcm_stride", ctypes.c_uint32),
    ]


class EncoderPlan(ctypes.Structure):
    _fields_ = [
        ("encoded_samples_per_frame", ctypes.c_uint32),
        ("pcm_samples_per_frame", ctypes.c_uint32),
        ("frame_bytes", ctypes.c_uint32),
        ("encoder_bytes", ctypes.c_uint32),
    ]


class EncoderCandidate(ctypes.Structure):
    _fields_ = [
        ("encoder", ctypes.c_void_p),
        ("config", EncoderConfig),
        ("plan", EncoderPlan),
    ]


class RuntimeLiblc3EncoderCandidateTests(unittest.TestCase):
    OK = 0
    INVALID = -1
    STORAGE_TOO_SMALL = -2
    PCM_TOO_SHORT = -3
    OUTPUT_TOO_SMALL = -4

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required for candidate qualification")

        cls.temporary = tempfile.TemporaryDirectory(
            prefix="opencfw-liblc3-candidate-"
        )
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "liblc3-candidate.dylib"
            if sys.platform == "darwin"
            else "liblc3-candidate.so"
        )
        command = [
            cls.clang,
            "-std=c11",
            "-O2",
            "-ffast-math",
            "-fshort-enums",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(UPSTREAM_INCLUDE),
            "-I",
            str(UPSTREAM_SRC),
            "-I",
            str(COMPONENT),
            str(SOURCE),
            *(str(path) for path in UPSTREAM_SOURCES),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-lm", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))

        cls.plan = cls.library.open_cfw_liblc3_encoder_plan
        cls.plan.argtypes = [
            ctypes.POINTER(EncoderConfig),
            ctypes.POINTER(EncoderPlan),
        ]
        cls.plan.restype = ctypes.c_int
        cls.setup = cls.library.open_cfw_liblc3_encoder_setup
        cls.setup.argtypes = [
            ctypes.POINTER(EncoderCandidate),
            ctypes.POINTER(EncoderConfig),
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        cls.setup.restype = ctypes.c_int
        cls.encode = cls.library.open_cfw_liblc3_encoder_encode
        cls.encode.argtypes = [
            ctypes.POINTER(EncoderCandidate),
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_void_p,
            ctypes.c_size_t,
        ]
        cls.encode.restype = ctypes.c_int

        cls.direct_setup = cls.library.lc3_setup_encoder
        cls.direct_setup.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
        ]
        cls.direct_setup.restype = ctypes.c_void_p
        cls.direct_encode = cls.library.lc3_encode
        cls.direct_encode.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
        ]
        cls.direct_encode.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    @staticmethod
    def config(**overrides: int) -> EncoderConfig:
        values = {
            "frame_us": 10_000,
            "sample_rate_hz": 16_000,
            "pcm_sample_rate_hz": 0,
            "bitrate_bps": 32_000,
            "pcm_format": 0,
            "pcm_stride": 1,
        }
        values.update(overrides)
        return EncoderConfig(**values)

    def make_plan(self, config: EncoderConfig) -> EncoderPlan:
        plan = EncoderPlan()
        self.assertEqual(self.plan(ctypes.byref(config), ctypes.byref(plan)), 0)
        return plan

    @staticmethod
    def aligned_storage(size: int) -> ctypes.Array[ctypes.c_uint64]:
        return (ctypes.c_uint64 * ((size + 7) // 8))()

    def test_geometry_and_fixed_width_boundary(self) -> None:
        self.assertEqual(ctypes.sizeof(EncoderConfig), 24)
        self.assertEqual(ctypes.sizeof(EncoderPlan), 16)
        self.assertEqual(
            [getattr(EncoderConfig, name).offset for name, _ in EncoderConfig._fields_],
            [0, 4, 8, 12, 16, 20],
        )

        expected_samples = {
            8_000: 80,
            16_000: 160,
            24_000: 240,
            32_000: 320,
            48_000: 480,
        }
        for sample_rate, samples in expected_samples.items():
            with self.subTest(sample_rate=sample_rate):
                plan = self.make_plan(self.config(sample_rate_hz=sample_rate))
                self.assertEqual(plan.encoded_samples_per_frame, samples)
                self.assertEqual(plan.pcm_samples_per_frame, samples)
                self.assertEqual(plan.frame_bytes, 40)
                self.assertGreater(plan.encoder_bytes, 0)

        resampled = self.make_plan(
            self.config(sample_rate_hz=16_000, pcm_sample_rate_hz=48_000)
        )
        self.assertEqual(resampled.encoded_samples_per_frame, 160)
        self.assertEqual(resampled.pcm_samples_per_frame, 480)

    def test_invalid_configurations_fail_before_storage_mutation(self) -> None:
        invalid = (
            self.config(frame_us=6_000),
            self.config(sample_rate_hz=44_100),
            self.config(sample_rate_hz=48_000, pcm_sample_rate_hz=16_000),
            self.config(pcm_format=4),
            self.config(pcm_stride=0),
            self.config(bitrate_bps=0xFFFFFFFF),
        )
        for config in invalid:
            config_values = tuple(
                getattr(config, name) for name, _ in EncoderConfig._fields_
            )
            with self.subTest(config=config_values):
                plan = EncoderPlan(0xA5, 0xA5, 0xA5, 0xA5)
                self.assertEqual(
                    self.plan(ctypes.byref(config), ctypes.byref(plan)),
                    self.INVALID,
                )
                self.assertEqual(
                    tuple(getattr(plan, name) for name, _ in EncoderPlan._fields_),
                    (0xA5, 0xA5, 0xA5, 0xA5),
                )

    def test_setup_enforces_storage_size_alignment_and_g2_enum_layout(self) -> None:
        config = self.config()
        plan = self.make_plan(config)
        storage = self.aligned_storage(plan.encoder_bytes)
        candidate = EncoderCandidate()

        self.assertEqual(
            self.setup(
                ctypes.byref(candidate),
                ctypes.byref(config),
                storage,
                plan.encoder_bytes - 1,
            ),
            self.STORAGE_TOO_SMALL,
        )
        self.assertFalse(candidate.encoder)
        self.assertEqual(
            self.setup(
                ctypes.byref(candidate),
                ctypes.byref(config),
                ctypes.c_void_p(ctypes.addressof(storage) + 1),
                plan.encoder_bytes,
            ),
            self.INVALID,
        )

        self.assertEqual(
            self.setup(
                ctypes.byref(candidate),
                ctypes.byref(config),
                storage,
                ctypes.sizeof(storage),
            ),
            self.OK,
        )
        self.assertEqual(candidate.encoder, ctypes.addressof(storage))
        # dt=10 ms, sr=16 kHz, sr_pcm=16 kHz at the stock byte offsets.
        self.assertEqual(bytes(storage)[:3], bytes((3, 1, 1)))

    def test_bounded_encode_matches_pristine_upstream_call(self) -> None:
        config = self.config(pcm_stride=2)
        plan = self.make_plan(config)
        candidate_storage = self.aligned_storage(plan.encoder_bytes)
        direct_storage = self.aligned_storage(plan.encoder_bytes)
        candidate = EncoderCandidate()
        self.assertEqual(
            self.setup(
                ctypes.byref(candidate),
                ctypes.byref(config),
                candidate_storage,
                ctypes.sizeof(candidate_storage),
            ),
            self.OK,
        )
        direct_encoder = self.direct_setup(
            config.frame_us,
            config.sample_rate_hz,
            config.pcm_sample_rate_hz,
            direct_storage,
        )
        self.assertEqual(direct_encoder, ctypes.addressof(direct_storage))

        required = (plan.pcm_samples_per_frame - 1) * config.pcm_stride + 1
        pcm = (ctypes.c_int16 * required)()
        for index in range(plan.pcm_samples_per_frame):
            pcm[index * config.pcm_stride] = ((index * 997) % 20_001) - 10_000
        candidate_output = (ctypes.c_uint8 * plan.frame_bytes)()
        direct_output = (ctypes.c_uint8 * plan.frame_bytes)()

        self.assertEqual(
            self.encode(
                ctypes.byref(candidate),
                pcm,
                required - 1,
                candidate_output,
                plan.frame_bytes,
            ),
            self.PCM_TOO_SHORT,
        )
        self.assertEqual(
            self.encode(
                ctypes.byref(candidate),
                pcm,
                required,
                candidate_output,
                plan.frame_bytes - 1,
            ),
            self.OUTPUT_TOO_SMALL,
        )
        self.assertEqual(
            self.encode(
                ctypes.byref(candidate),
                pcm,
                required,
                candidate_output,
                plan.frame_bytes,
            ),
            self.OK,
        )
        self.assertEqual(
            self.direct_encode(
                direct_encoder,
                config.pcm_format,
                pcm,
                config.pcm_stride,
                plan.frame_bytes,
                direct_output,
            ),
            0,
        )
        self.assertEqual(bytes(candidate_output), bytes(direct_output))
        self.assertNotEqual(bytes(candidate_output), bytes(plan.frame_bytes))

    def test_all_four_authenticated_pcm_loader_slots_match_upstream(self) -> None:
        for pcm_format in range(4):
            with self.subTest(pcm_format=pcm_format):
                config = self.config(pcm_format=pcm_format)
                plan = self.make_plan(config)
                candidate_storage = self.aligned_storage(plan.encoder_bytes)
                direct_storage = self.aligned_storage(plan.encoder_bytes)
                candidate = EncoderCandidate()
                self.assertEqual(
                    self.setup(
                        ctypes.byref(candidate),
                        ctypes.byref(config),
                        candidate_storage,
                        ctypes.sizeof(candidate_storage),
                    ),
                    self.OK,
                )
                direct_encoder = self.direct_setup(
                    config.frame_us,
                    config.sample_rate_hz,
                    config.pcm_sample_rate_hz,
                    direct_storage,
                )

                values = [
                    ((index * 997) % 20_001) - 10_000
                    for index in range(plan.pcm_samples_per_frame)
                ]
                if pcm_format == 0:
                    pcm = (ctypes.c_int16 * len(values))(*values)
                elif pcm_format == 1:
                    pcm = (ctypes.c_int32 * len(values))(
                        *(value << 8 for value in values)
                    )
                elif pcm_format == 2:
                    pcm = (ctypes.c_uint8 * (3 * len(values)))()
                    for index, value in enumerate(values):
                        packed = (value << 8) & 0xFFFFFF
                        pcm[3 * index + 0] = packed & 0xFF
                        pcm[3 * index + 1] = (packed >> 8) & 0xFF
                        pcm[3 * index + 2] = (packed >> 16) & 0xFF
                else:
                    pcm = (ctypes.c_float * len(values))(
                        *(value / 10_000.0 for value in values)
                    )

                candidate_output = (ctypes.c_uint8 * plan.frame_bytes)()
                direct_output = (ctypes.c_uint8 * plan.frame_bytes)()
                self.assertEqual(
                    self.encode(
                        ctypes.byref(candidate),
                        pcm,
                        len(values),
                        candidate_output,
                        plan.frame_bytes,
                    ),
                    self.OK,
                )
                self.assertEqual(
                    self.direct_encode(
                        direct_encoder,
                        pcm_format,
                        pcm,
                        1,
                        plan.frame_bytes,
                        direct_output,
                    ),
                    0,
                )
                self.assertEqual(bytes(candidate_output), bytes(direct_output))

    def test_short_enum_gate_rejects_the_default_target_abi(self) -> None:
        output = Path(self.temporary.name) / "bad-enum-abi.o"
        command = [
            self.clang,
            *(flag for flag in TARGET_FLAGS if flag != "-fshort-enums"),
            "-I",
            str(TARGET_COMPAT),
            "-I",
            str(UPSTREAM_INCLUDE),
            "-I",
            str(UPSTREAM_SRC),
            "-I",
            str(COMPONENT),
            "-c",
            str(SOURCE),
            "-o",
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("G2 liblc3 requires -fshort-enums", result.stderr)

    def test_complete_upstream_snapshot_and_adapter_compile_for_cortex_m55(self) -> None:
        output_directory = Path(self.temporary.name) / "target"
        output_directory.mkdir()
        for source in (*UPSTREAM_SOURCES, SOURCE):
            with self.subTest(source=source.name):
                output = output_directory / f"{source.stem}.o"
                subprocess.run(
                    [
                        self.clang,
                        *TARGET_FLAGS,
                        "-I",
                        str(TARGET_COMPAT),
                        "-I",
                        str(UPSTREAM_INCLUDE),
                        "-I",
                        str(UPSTREAM_SRC),
                        "-I",
                        str(COMPONENT),
                        "-c",
                        str(source),
                        "-o",
                        str(output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertGreater(output.stat().st_size, 0)

    def test_snapshot_authentication_license_and_production_exclusion(self) -> None:
        subprocess.run(
            [sys.executable, str(UPSTREAM / "verify_snapshot.py")],
            check=True,
            cwd=UPSTREAM,
            capture_output=True,
            text=True,
        )
        self.assertIn("SPDX-License-Identifier: Apache-2.0", SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: Apache-2.0", HEADER.read_text())
        overlay = (
            ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
        ).read_text()
        self.assertNotIn("runtime_liblc3_encoder_candidate", overlay)


if __name__ == "__main__":
    unittest.main()
