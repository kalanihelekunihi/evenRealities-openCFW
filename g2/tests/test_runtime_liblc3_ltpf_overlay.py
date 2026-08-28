"""Software-only admission tests for the production liblc3 LTPF overlay."""

from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "apollo_main" / "liblc3_ltpf"
CONFIG = json.loads((COMPONENT / "overlay.json").read_text(encoding="utf-8"))
BUILDER_PATH = COMPONENT / "build_component.py"
SPEC = importlib.util.spec_from_file_location("liblc3_ltpf_builder", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class Liblc3LtpfOverlayTest(unittest.TestCase):
    def test_source_and_license_pins(self) -> None:
        for record in CONFIG["sources"]:
            path = ROOT / record["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), record["size"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), record["sha256"])
            self.assertEqual(record["license"], "Apache-2.0")
        license_text = (ROOT / "third_party" / "liblc3" / "LICENSE").read_text(
            encoding="utf-8"
        )
        self.assertIn("Apache License", license_text)
        self.assertIn("TERMS AND CONDITIONS", license_text)

    def test_both_reviewed_toolchain_profiles(self) -> None:
        profiles = (
            ("apple-clang", Path("/usr/bin/clang")),
            ("linux-clang", Path("/opt/homebrew/opt/llvm@22/bin/clang")),
        )
        validated = []
        for profile, compiler in profiles:
            if not compiler.is_file():
                continue
            first_line = subprocess.run(
                [str(compiler), "--version"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()[0]
            if not first_line.startswith(
                CONFIG["profiles"][profile]["reviewed_version_prefix"]
            ):
                continue
            with tempfile.TemporaryDirectory(prefix=f"open-cfw-{profile}-") as directory:
                report = BUILDER.build(
                    config_path=COMPONENT / "overlay.json",
                    output_dir=Path(directory),
                    clang=str(compiler),
                    profile=profile,
                    record=False,
                )
            expected = CONFIG["profiles"][profile]
            self.assertEqual(report["overlay"]["size"], expected["overlay"]["size"])
            self.assertEqual(report["overlay"]["sha256"], expected["overlay"]["sha256"])
            self.assertEqual(report["component"]["size"], expected["component"]["size"])
            self.assertEqual(report["component"]["sha256"], expected["component"]["sha256"])
            self.assertEqual(report["overlay"]["runtime_dependencies"], [])
            self.assertEqual(len(report["overlay"]["text_relocations"]), 16)
            self.assertEqual(len(report["overlay"]["dispatch_entries"]), 7)
            self.assertEqual(report["overlay"]["dispatch_entries"][4]["target"],
                             report["overlay"]["dispatch_entries"][5]["target"])
            validated.append(profile)
        if Path("/usr/bin/clang").is_file() and Path(
            "/opt/homebrew/opt/llvm@22/bin/clang"
        ).is_file():
            self.assertEqual(validated, ["apple-clang", "linux-clang"])

    def test_patch_is_single_authenticated_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-liblc3-route-") as directory:
            report = BUILDER.build(
                config_path=COMPONENT / "overlay.json",
                output_dir=Path(directory),
                clang="/usr/bin/clang",
                profile="apple-clang",
                record=False,
            )
            component = (Path(directory) / "ota_s200_firmware_ota.bin").read_bytes()
        base = (ROOT / CONFIG["base"]["path"]).read_bytes()
        patch = report["patch_site"]
        patch_offset = patch["file_offset"]
        self.assertEqual(base[patch_offset:patch_offset + 4].hex(), "a7f6acfd")
        self.assertEqual(component[patch_offset:patch_offset + 4].hex(), "02f262ff")
        self.assertEqual(patch["decoded_target"], report["placement"]["entry"])
        for start, size in ((0x00438400, 260), (0x00438604, 364)):
            offset = start - CONFIG["run_base"] + CONFIG["preamble_bytes"]
            self.assertEqual(component[offset:offset + size], base[offset:offset + size])
        self.assertFalse(report["historical_non_corpus_routing"]["0x00438400"])
        self.assertFalse(report["historical_non_corpus_routing"]["0x00438604"])

    def test_runtime_memmove_and_nonnegative_sqrt(self) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            self.skipTest("host C compiler unavailable")
        with tempfile.TemporaryDirectory(prefix="open-cfw-liblc3-runtime-") as directory:
            library = Path(directory) / "runtime.dylib"
            subprocess.run(
                [
                    compiler,
                    "-shared",
                    "-fPIC",
                    "-O2",
                    "-DOPEN_CFW_LIBLC3_RUNTIME_ONLY=1",
                    str(COMPONENT / "liblc3_ltpf_overlay.c"),
                    "-o",
                    str(library),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            runtime = ctypes.CDLL(str(library))
            memmove = runtime.open_cfw_liblc3_memmove
            memmove.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            memmove.restype = ctypes.c_void_p
            sqrtf = runtime.open_cfw_liblc3_sqrtf_nonnegative
            sqrtf.argtypes = [ctypes.c_float]
            sqrtf.restype = ctypes.c_float

            for source in range(0, 17):
                for destination in range(0, 17):
                    for count in range(0, 33 - max(source, destination)):
                        initial = bytearray(range(33))
                        expected = initial[:]
                        expected[destination:destination + count] = initial[source:source + count]
                        storage = (ctypes.c_ubyte * len(initial)).from_buffer_copy(initial)
                        base = ctypes.addressof(storage)
                        returned = memmove(base + destination, base + source, count)
                        self.assertEqual(returned, base + destination)
                        self.assertEqual(bytes(storage), bytes(expected))

            for value in (0.0, 1.0, 2.0, 17.0, 65536.0, float("inf")):
                observed = float(sqrtf(value))
                expected = math.sqrt(value)
                if math.isinf(expected):
                    self.assertTrue(math.isinf(observed))
                else:
                    self.assertAlmostEqual(observed, expected, places=6)
            self.assertTrue(math.isnan(float(sqrtf(-1.0))))


if __name__ == "__main__":
    unittest.main()
