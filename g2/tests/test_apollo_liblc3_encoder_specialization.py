#!/usr/bin/env python3
"""Qualification for the unplaced Apollo liblc3 specialization experiment."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from g2.tests import test_runtime_liblc3_encoder_provider as provider_test
except ModuleNotFoundError:
    from tests import test_runtime_liblc3_encoder_provider as provider_test


SHARED_COMPONENT = provider_test.COMPONENT
Config = provider_test.Config
HOST_SOURCES = provider_test.HOST_SOURCES
Plan = provider_test.Plan
Provider = provider_test.Provider
UPSTREAM_INCLUDE = provider_test.UPSTREAM_INCLUDE
UPSTREAM_SRC = provider_test.UPSTREAM_SRC


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
BUILDER = COMPONENT / "build_specialization_experiment.py"
MANIFEST = COMPONENT / "specialization_experiment.json"
ANALYZER = G2 / "tools/analyze_g2_liblc3_encoder_specialization.py"
PROVIDER_SOURCE = SHARED_COMPONENT / "runtime_liblc3_encoder_provider.c"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloLiblc3EncoderSpecializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or "/usr/bin/clang"
        cls.lld = os.environ.get("OPENCFW_LLD") or "/opt/homebrew/bin/ld.lld"
        if not Path(cls.clang).is_file() or not Path(cls.lld).is_file():
            raise unittest.SkipTest("reviewed Apple Clang/LLD profile unavailable")
        cls.analyzer = load_module(
            ANALYZER, "analyze_g2_liblc3_encoder_specialization_test"
        )
        cls.audit = cls.analyzer.run_audit()

    def test_runtime_state_limits_specialization_to_non_hr(self) -> None:
        service = self.audit["service_audio_configuration"]
        self.assertEqual(service["contexts"], [
            "0x20106A7C", "0x201074C0", "0x20107F04", "0x20108948",
        ])
        self.assertEqual(service["known"], {
            "hrmode": False,
            "pcm_sample_rate_hz_argument": 0,
            "pcm_sample_rate_normalizes_to_encoded_rate": True,
        })
        self.assertEqual(set(service["runtime_unproven"]), {
            "pcm_format", "frame_us", "sample_rate_hz", "channels_or_stride",
            "channel_offset", "bitrate_bps",
        })
        self.assertFalse(
            self.audit["outcome"]["exact_runtime_configuration_derived"]
        )

    def test_size_reduction_is_real_but_does_not_fit(self) -> None:
        baseline = self.audit["baseline"]
        admitted = self.audit["admitted_non_hr_only"]
        self.assertEqual(
            (baseline["text"], baseline["rodata"], baseline["data"]),
            (43248, 85088, 404),
        )
        self.assertEqual(admitted["section_deltas"], {
            "text": 2368, "rodata": 24772, "data": 0,
        })
        self.assertEqual(admitted["aligned_span"], 101616)
        self.assertEqual(admitted["shortfall"], 30516)
        self.assertFalse(admitted["fits_authenticated_headroom"])
        rejected = self.audit["rejected_duration_counterfactual"]
        self.assertFalse(rejected["evidence_admitted"])
        self.assertEqual(rejected["shortfall"], 21076)

    def test_two_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="liblc3-spec-a-") as first, \
                tempfile.TemporaryDirectory(prefix="liblc3-spec-b-") as second:
            reports = []
            for output in (first, second):
                completed = subprocess.run([
                    sys.executable, str(BUILDER), "--config", str(MANIFEST),
                    "--output-dir", output, "--clang", self.clang,
                    "--lld", self.lld,
                ], cwd=G2, check=True, capture_output=True, text=True)
                reports.append(json.loads(completed.stdout))
            self.assertEqual(reports[0], reports[1])
            first_files = sorted(
                path.relative_to(first) for path in Path(first).rglob("*")
                if path.is_file()
            )
            second_files = sorted(
                path.relative_to(second) for path in Path(second).rglob("*")
                if path.is_file()
            )
            self.assertEqual(first_files, second_files)
            self.assertEqual(first_files, [
                Path("build-report.json"),
                Path("non_hr_only/liblc3_encoder.pre-policy.o"),
                Path("non_hr_only/liblc3_encoder.relocatable.o"),
                Path("non_hr_only/liblc3_encoder.rodata.bin"),
                Path("non_hr_only/liblc3_encoder.table_rodata.relocatable.bin"),
                Path("non_hr_only/liblc3_encoder.text.bin"),
                Path("non_hr_only/qualification-final/liblc3_encoder.qualification-final.elf"),
                Path("non_hr_only/qualification-final/liblc3_encoder.rodata.qualification-xip.bin"),
                Path("non_hr_only/qualification-final/liblc3_encoder.table_rodata.qualification-xip.bin"),
                Path("non_hr_only/qualification-final/liblc3_encoder.text.qualification-xip.bin"),
                Path("standard_duration_only_counterfactual/liblc3_encoder.data.bin"),
                Path("standard_duration_only_counterfactual/liblc3_encoder.relocatable.o"),
                Path("standard_duration_only_counterfactual/liblc3_encoder.rodata.bin"),
                Path("standard_duration_only_counterfactual/liblc3_encoder.text.bin"),
            ])
            for relative in first_files:
                self.assertEqual(
                    (Path(first) / relative).read_bytes(),
                    (Path(second) / relative).read_bytes(),
                    relative,
                )
            admitted = reports[0]["variants"]["non_hr_only"]
            self.assertEqual(
                admitted["receipt"]["linked_object"]["sha256"],
                "bc548b0578f87d43c38def5fb727533a73d7e2f31105e5e8bd0d0a1fef336b7d",
            )
            self.assertEqual(
                admitted["receipt"]["artifacts"]["table_rodata"], {
                    "size": 404,
                    "sha256":
                        "c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a",
                })
            relocation = admitted["qualification_finalization"][
                "relocation_application"]
            self.assertEqual(relocation["input_table_initializers"], 78)
            self.assertEqual(relocation["input_table_code_references"], 12)
            self.assertEqual(relocation["output_relocations"], 0)
            self.assertTrue(relocation["xip_emission_after_validation"])
            self.assertFalse(admitted["qualification_finalization"][
                "production_placement"])
            self.assertFalse(
                reports[0]["outcome"][
                    "admitted_variant_fits_authenticated_headroom"]
            )

    def test_evidence_promotion_fails_before_compile(self) -> None:
        config = json.loads(MANIFEST.read_text(encoding="utf-8"))
        config["variants"]["non_hr_only"]["compile_defines"] = [
            "-DLC3_PLUS_HR=0", "-DLC3_PLUS=0",
        ]
        with tempfile.TemporaryDirectory(prefix="liblc3-spec-tamper-") as d:
            tampered = Path(d) / "specialization.json"
            tampered.write_text(json.dumps(config), encoding="utf-8")
            completed = subprocess.run([
                sys.executable, str(BUILDER), "--config", str(tampered),
                "--output-dir", str(Path(d) / "out"),
                "--clang", self.clang, "--lld", self.lld,
            ], cwd=G2, capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "admitted non-HR specialization contract drift",
                completed.stderr,
            )

    @staticmethod
    def _bind(library: Path):
        lib = ctypes.CDLL(str(library))
        plan = lib.open_cfw_liblc3_encoder_provider_plan
        plan.argtypes = [ctypes.POINTER(Config), ctypes.POINTER(Plan)]
        plan.restype = ctypes.c_int
        setup = lib.open_cfw_liblc3_encoder_provider_setup
        setup.argtypes = [ctypes.POINTER(Provider), ctypes.POINTER(Config),
                          ctypes.c_void_p, ctypes.c_size_t]
        setup.restype = ctypes.c_int
        encode = lib.open_cfw_liblc3_encoder_provider_encode
        encode.argtypes = [ctypes.POINTER(Provider), ctypes.c_void_p,
                           ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
        encode.restype = ctypes.c_int
        return plan, setup, encode

    def _compile_host(self, output: Path, defines: list[str]) -> None:
        command = [
            self.clang, "-std=c11", "-O2", "-ffast-math", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", *defines,
            "-I", str(UPSTREAM_INCLUDE), "-I", str(UPSTREAM_SRC),
            "-I", str(SHARED_COMPONENT), str(PROVIDER_SOURCE),
            *(str(path) for path in HOST_SOURCES),
        ]
        command += (["-dynamiclib", "-o", str(output)]
                    if sys.platform == "darwin"
                    else ["-shared", "-fPIC", "-lm", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)

    @staticmethod
    def _run_one(bound, config: Config):
        plan_call, setup, encode = bound
        plan = Plan()
        if plan_call(ctypes.byref(config), ctypes.byref(plan)) != 0:
            return None
        storage = (ctypes.c_uint64 * ((plan.encoder_bytes + 7) // 8))()
        provider = Provider()
        if setup(ctypes.byref(provider), ctypes.byref(config), storage,
                 ctypes.sizeof(storage)) != 0:
            raise AssertionError("host provider setup failed")
        pcm = provider_test.RuntimeLiblc3EncoderProviderTests.pcm_for(
            config.pcm_format, plan.pcm_samples_per_frame, config.pcm_stride
        )
        output = (ctypes.c_uint8 * plan.frame_bytes)()
        if encode(ctypes.byref(provider), pcm, ctypes.sizeof(pcm), output,
                  plan.frame_bytes) != 0:
            raise AssertionError("host provider encode failed")
        return bytes(plan), bytes(output)

    def test_non_hr_build_matches_baseline_for_complete_dynamic_grid(self) -> None:
        with tempfile.TemporaryDirectory(prefix="liblc3-spec-host-") as d:
            extension = ".dylib" if sys.platform == "darwin" else ".so"
            baseline = Path(d) / f"baseline{extension}"
            specialized = Path(d) / f"specialized{extension}"
            self._compile_host(baseline, [])
            self._compile_host(specialized, ["-DLC3_PLUS_HR=0"])
            baseline_calls = self._bind(baseline)
            specialized_calls = self._bind(specialized)
            for duration in (2500, 5000, 7500, 10000):
                for rate in (8000, 16000, 24000, 32000, 48000):
                    for pcm_format in range(4):
                        config = Config(
                            frame_us=duration, sample_rate_hz=rate,
                            pcm_sample_rate_hz=0, bitrate_bps=32000,
                            pcm_format=pcm_format, pcm_stride=2,
                        )
                        with self.subTest(duration=duration, rate=rate,
                                          pcm_format=pcm_format):
                            self.assertEqual(
                                self._run_one(baseline_calls, config),
                                self._run_one(specialized_calls, config),
                            )
            for bitrate in (16000, 32000, 64000, 128000):
                config = Config(
                    frame_us=10000, sample_rate_hz=16000,
                    pcm_sample_rate_hz=48000, bitrate_bps=bitrate,
                    pcm_format=0, pcm_stride=1,
                )
                with self.subTest(bitrate=bitrate):
                    self.assertEqual(
                        self._run_one(baseline_calls, config),
                        self._run_one(specialized_calls, config),
                    )


if __name__ == "__main__":
    unittest.main()
