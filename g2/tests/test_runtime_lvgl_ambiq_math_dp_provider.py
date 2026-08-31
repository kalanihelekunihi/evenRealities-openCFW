#!/usr/bin/env python3
"""Reference, hostile-input, ABI, and manifest gates for FPv5-D16 math."""

from __future__ import annotations

import ctypes
import json
import math
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"
MUSL = RUNTIME / "musl-math"
WRAPPER = RUNTIME / "lvgl_ambiq_math_dp_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_math_dp_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"
SYMBOLS = {"cosf", "sinf", "sqrt", "tanf"}
SOURCES = (
    ("cosf", ["-Dcosf=open_cfw_musl_cosf"]),
    ("sinf", ["-Dsinf=open_cfw_musl_sinf"]),
    ("tanf", ["-Dtanf=open_cfw_musl_tanf"]),
    ("__cosdf", []),
    ("__sindf", []),
    ("__tandf", []),
    ("__rem_pio2f", []),
    ("__rem_pio2_large", []),
    ("floor", []),
    ("scalbn", []),
    ("sqrt", ["-Dsqrt=open_cfw_musl_sqrt"]),
    ("sqrt_data", []),
    ("__math_invalid", []),
)
INTERNAL_DEFINITIONS = (
    "-D__cosdf=open_cfw_musl_cos_kernel",
    "-D__sindf=open_cfw_musl_sin_kernel",
    "-D__tandf=open_cfw_musl_tan_kernel",
    "-D__rem_pio2f=open_cfw_musl_rem_pio2f",
    "-D__rem_pio2_large=open_cfw_musl_rem_pio2_large",
    "-D__math_invalid=open_cfw_musl_math_invalid",
    "-D__rsqrt_tab=open_cfw_musl_rsqrt_tab",
    "-Dfloor=open_cfw_musl_floor",
    "-Dscalbn=open_cfw_musl_scalbn",
)


def as_float32(value: float) -> float:
    return struct.unpack("=f", struct.pack("=f", value))[0]


def float32_ulp_distance(left: float, right: float) -> int:
    def ordered(value: float) -> int:
        bits = struct.unpack("=I", struct.pack("=f", value))[0]
        return (~bits & 0xFFFFFFFF) if bits >> 31 else (bits | 0x80000000)
    return abs(ordered(left) - ordered(right))


def float64_ulp_distance(left: float, right: float) -> int:
    def ordered(value: float) -> int:
        bits = struct.unpack("=Q", struct.pack("=d", value))[0]
        return (~bits & 0xFFFFFFFFFFFFFFFF) if bits >> 63 else (bits | (1 << 63))
    return abs(ordered(left) - ordered(right))


class MathDPProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-math-dp-provider-")
        cls.library = cls._build_shared_library()
        cls.library.cosf.argtypes = [ctypes.c_float]
        cls.library.cosf.restype = ctypes.c_float
        cls.library.sinf.argtypes = [ctypes.c_float]
        cls.library.sinf.restype = ctypes.c_float
        cls.library.sqrt.argtypes = [ctypes.c_double]
        cls.library.sqrt.restype = ctypes.c_double
        cls.library.tanf.argtypes = [ctypes.c_float]
        cls.library.tanf.restype = ctypes.c_float

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def _compile_objects(cls, directory: Path, extra: list[str]) -> list[Path]:
        common = [
            cls.clang, "-std=gnu11", "-O1", "-g", "-fno-builtin",
            "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror",
            "-I", str(MUSL), "-I", str(RUNTIME), *extra,
        ]
        objects = []
        for name, definitions in SOURCES:
            obj = directory / f"{name}.o"
            subprocess.run([
                *common, *INTERNAL_DEFINITIONS, *definitions,
                "-c", str(MUSL / f"{name}.c"), "-o", str(obj),
            ], cwd=ROOT, check=True, capture_output=True, text=True)
            objects.append(obj)
        wrapper = directory / "wrapper.o"
        subprocess.run(
            [*common, "-c", str(WRAPPER), "-o", str(wrapper)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        objects.append(wrapper)
        return objects

    @classmethod
    def _build_shared_library(cls) -> ctypes.CDLL:
        directory = Path(cls.temporary.name) / "shared"
        directory.mkdir()
        objects = cls._compile_objects(directory, ["-fPIC"])
        library = directory / ("provider.dylib" if sys.platform == "darwin" else "provider.so")
        mode = "-dynamiclib" if sys.platform == "darwin" else "-shared"
        subprocess.run(
            [cls.clang, mode, *map(str, objects), "-lm", "-o", str(library)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        return ctypes.CDLL(str(library))

    def test_deterministic_full_range_reference_oracle(self) -> None:
        rng = random.Random(0x5109_3009)
        for _ in range(10_000):
            bits = rng.getrandbits(32)
            x = struct.unpack("=f", struct.pack("=I", bits))[0]
            if math.isfinite(x):
                for symbol, reference in (
                    ("cosf", math.cos), ("sinf", math.sin), ("tanf", math.tan),
                ):
                    observed = getattr(self.library, symbol)(x)
                    expected = as_float32(reference(x))
                    self.assertLessEqual(
                        float32_ulp_distance(observed, expected), 1,
                        f"{symbol}({x!r})",
                    )

            exponent = rng.randint(-1074, 1023)
            significand = rng.uniform(0.5, 1.0)
            value = math.ldexp(significand, exponent)
            observed_sqrt = self.library.sqrt(value)
            expected_sqrt = math.sqrt(value)
            self.assertLessEqual(
                float64_ulp_distance(observed_sqrt, expected_sqrt), 1,
                f"sqrt({value!r})",
            )

    def test_hostile_fixture_is_sanitizer_clean(self) -> None:
        directory = Path(self.temporary.name) / "sanitizer"
        directory.mkdir()
        sanitize = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        objects = self._compile_objects(directory, sanitize)
        executable = directory / "hostile"
        subprocess.run([
            self.clang, *sanitize, "-Wall", "-Wextra", "-Werror",
            "-I", str(RUNTIME), *map(str, objects), str(FIXTURE),
            "-lm", "-o", str(executable),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_exact_target_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_math_dp_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-math-dp-provider.o", "size": 13_144,
            "sha256": "3b67eea354a8f12f48faed3177b9d170fa7c8191ced9e30803cbe6b31b2e8c8a",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_math_dp_provider_abi.o", "size": 2_240,
            "sha256": "c7122f705fa35d40f468d4bbc9e68c56746fc6da089639e7526a639add3bf354",
        })
        self.assertEqual(set(provider["required_exports"]), SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertEqual(provider["closed_consumer_relocation_count"], 35)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_upstream_and_residual_boundaries_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_math_dp_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["tag"], "v1.2.5")
        self.assertEqual(upstream["commit"], "0784374d561435f7c787a555aeab8ede699ed298")
        self.assertEqual(len(upstream["source_git_blobs"]), 14)
        self.assertEqual(set(provider["closed_consumer_relocations"]), SYMBOLS)
        self.assertEqual(report["missing_provider_count"], 11)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(SYMBOLS.isdisjoint(missing))


if __name__ == "__main__":
    unittest.main()
