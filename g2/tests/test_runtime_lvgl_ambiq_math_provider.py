#!/usr/bin/env python3
"""Numerical, hostile-input, ABI, and manifest gates for the math provider."""

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
PATCH = ROOT / "third_party/lvgl-ambiq-backend/g2-compat/musl-math-failclosed.patch"
WRAPPER = RUNTIME / "lvgl_ambiq_math_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_math_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"
SYMBOLS = {"acosf", "atan2f", "atanf", "fmod", "fmodf"}
DEFINITIONS = {
    "acosf": ["-Dacosf=open_cfw_musl_acosf", "-Dsqrtf=open_cfw_musl_sqrtf"],
    "atan2f": ["-Datan2f=open_cfw_musl_atan2f", "-Datanf=open_cfw_musl_atanf"],
    "atanf": ["-Datanf=open_cfw_musl_atanf"],
    "fmod": ["-Dfmod=open_cfw_musl_fmod"],
    "fmodf": ["-Dfmodf=open_cfw_musl_fmodf"],
}


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


class MathProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-math-provider-")
        cls.stage = Path(cls.temporary.name) / "stage"
        cls.stage.mkdir()
        for name in DEFINITIONS:
            shutil.copy2(MUSL / f"{name}.c", cls.stage / f"{name}.c")
        subprocess.run(
            ["patch", "-s", "-p1", "-i", str(PATCH)],
            cwd=cls.stage, check=True, capture_output=True, text=True,
        )
        cls.library = cls._build_shared_library()
        cls._configure(cls.library)

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
        for name, definitions in DEFINITIONS.items():
            obj = directory / f"{name}.o"
            subprocess.run(
                [*common, *definitions, "-c", str(cls.stage / f"{name}.c"), "-o", str(obj)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
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

    @staticmethod
    def _configure(library: ctypes.CDLL) -> None:
        library.acosf.argtypes = [ctypes.c_float]
        library.acosf.restype = ctypes.c_float
        library.atan2f.argtypes = [ctypes.c_float, ctypes.c_float]
        library.atan2f.restype = ctypes.c_float
        library.atanf.argtypes = [ctypes.c_float]
        library.atanf.restype = ctypes.c_float
        library.fmod.argtypes = [ctypes.c_double, ctypes.c_double]
        library.fmod.restype = ctypes.c_double
        library.fmodf.argtypes = [ctypes.c_float, ctypes.c_float]
        library.fmodf.restype = ctypes.c_float

    def test_deterministic_randomized_reference_oracle(self) -> None:
        rng = random.Random(0x5109_3005)
        for _ in range(5_000):
            x = as_float32(math.ldexp(rng.uniform(-1.0, 1.0), rng.randint(-120, 120)))
            observed = self.library.atanf(x)
            expected = as_float32(math.atan(x))
            self.assertLessEqual(float32_ulp_distance(observed, expected), 1)

            y = as_float32(math.ldexp(rng.uniform(-1.0, 1.0), rng.randint(-120, 120)))
            if x != 0.0 or y != 0.0:
                observed = self.library.atan2f(y, x)
                expected = as_float32(math.atan2(y, x))
                self.assertLessEqual(float32_ulp_distance(observed, expected), 1)

            unit = as_float32(rng.uniform(-1.0, 1.0))
            observed = self.library.acosf(unit)
            expected = as_float32(math.acos(unit))
            self.assertLessEqual(float32_ulp_distance(observed, expected), 1)

            denominator = as_float32(math.ldexp(rng.uniform(0.5, 1.0), rng.randint(-120, 120)))
            numerator = as_float32(math.ldexp(rng.uniform(-1.0, 1.0), rng.randint(-120, 120)))
            if denominator != 0.0:
                observed = self.library.fmodf(numerator, denominator)
                expected = as_float32(math.fmod(numerator, denominator))
                self.assertLessEqual(float32_ulp_distance(observed, expected), 1)

            dx = math.ldexp(rng.uniform(-1.0, 1.0), rng.randint(-1020, 1020))
            dy = math.ldexp(rng.uniform(0.5, 1.0), rng.randint(-1020, 1020))
            observed = self.library.fmod(dx, dy)
            expected = math.fmod(dx, dy)
            self.assertLessEqual(float64_ulp_distance(observed, expected), 1)

    def test_hostile_fixture_is_sanitizer_clean(self) -> None:
        directory = Path(self.temporary.name) / "sanitizer"
        directory.mkdir()
        sanitize = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
        objects = self._compile_objects(directory, sanitize)
        executable = directory / "hostile"
        subprocess.run(
            [
                self.clang, *sanitize, "-Wall", "-Wextra", "-Werror",
                "-I", str(RUNTIME), *map(str, objects), str(FIXTURE),
                "-lm", "-o", str(executable),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_exact_target_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_math_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-math-provider.o", "size": 6_576,
            "sha256": "123f1163b67fa953c3a77aa9ce3da7652fa6aae1001dc206b9f742f75f14a1af",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_math_provider_abi.o", "size": 2_556,
            "sha256": "6cf6b2cde6c8035b10faf35fac4a1e6ef2e9b134d617548a2659a671f5cc222e",
        })
        self.assertEqual(set(provider["required_exports"]), SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertEqual(provider["closed_consumer_relocation_count"], 46)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_upstream_and_residual_boundaries_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        upstream = report["local_math_provider"]["authenticated_upstream"]
        self.assertEqual(upstream["tag"], "v1.2.5")
        self.assertEqual(upstream["commit"], "0784374d561435f7c787a555aeab8ede699ed298")
        self.assertEqual(len(upstream["source_git_blobs"]), 5)
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(SYMBOLS.isdisjoint(missing))


if __name__ == "__main__":
    unittest.main()
