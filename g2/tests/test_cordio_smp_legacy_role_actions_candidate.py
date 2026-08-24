#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "smpi": (
        ROOT / "components/apollo_main/core_overlay/cordio_smpi_act.c",
        ROOT / "tests/fixtures/cordio_smpi_act_host.c",
        16690,
        "0a19fb3adddd4ae6b9a71a4b012b2dea23cc3999938e3e6be1f8da4772a538df",
        10,
        "key_ready = 1U",
    ),
    "smpr": (
        ROOT / "components/apollo_main/core_overlay/cordio_smpr_act.c",
        ROOT / "tests/fixtures/cordio_smpr_act_host.c",
        16630,
        "f01027a9e7bc6e6af2bf4add1838cf873e1e90b6c2ee57e419e3a82f02dac5ed",
        10,
        "key_ready = 1U",
    ),
}


class CordioSmpLegacyRoleActionTests(unittest.TestCase):
    def test_source_pins_and_complete_action_sets(self):
        for role, (source, _fixture, size, digest, count, key_ready) in CASES.items():
            data = source.read_bytes()
            text = data.decode()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), (size, digest), role)
            self.assertEqual(text.count("__attribute__((noinline)) void open_cfw_cordio_"), count, role)
            self.assertIn(key_ready, text, role)
            self.assertIn("UINTPTR_MAX == 0xFFFFFFFFU", text, role)

    def test_host_behavior_and_strict_compilation(self):
        with tempfile.TemporaryDirectory() as temp:
            for role, (_source, fixture, *_rest) in CASES.items():
                output = Path(temp) / role
                subprocess.run([
                    "clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(fixture), "-o", str(output),
                ], check=True)
                subprocess.run([str(output)], check=True)

    def test_freestanding_thumb_compilation(self):
        with tempfile.TemporaryDirectory() as temp:
            for role, (source, _fixture, *_rest) in CASES.items():
                output = Path(temp) / f"{role}.o"
                subprocess.run([
                    "xcrun", "clang", "-target", "armv7m-none-eabi",
                    "-mcpu=cortex-m4", "-mthumb", "-Oz", "-ffreestanding",
                    "-fno-builtin", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-c", str(source), "-o", str(output),
                ], check=True)


if __name__ == "__main__":
    unittest.main()
