#!/usr/bin/env python3
"""Static qualification for the clean-room IAR memory-provider candidates."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/candidates/iar_runtime_memory.S"
EMULATOR = ROOT / "tools/emulate_g2_iar_memory.py"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
EXPECTED = {
    "open_cfw_iar_memcpy_void": (152, "ee2582dc5c82d4bd438403a2682be0debc10c301ec0549942b7c56baa61d026f"),
    "open_cfw_iar_memcpy_aligned_void": (152, "ee2582dc5c82d4bd438403a2682be0debc10c301ec0549942b7c56baa61d026f"),
    "open_cfw_iar_memmove_void": (322, "2dbb1c506a291cc94fc624d492c0b55cd09e011e317bb21fd31004ee40a965b5"),
}
TARGET_FLAGS = (
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
)


class IARRuntimeMemoryCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.temporary = tempfile.TemporaryDirectory(prefix="openCFW-iar-memory-")
        cls.output = Path(cls.temporary.name)
        compiler = subprocess.run(
            ["xcrun", "-f", "clang"], check=True, capture_output=True, text=True
        ).stdout.strip()
        cls.object = cls.output / "runtime.o"
        subprocess.run(
            [compiler, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.object)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.bodies = {}
        cls.metadata = {}
        for name in EXPECTED:
            body, metadata = apollo_overlay.extract_isolated_function_section(cls.object, name)
            cls.bodies[name] = body
            cls.metadata[name] = metadata
            (cls.output / f"{name}.bin").write_bytes(body)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_sections_are_dependency_free_and_byte_pinned(self) -> None:
        for name, (expected_size, expected_hash) in EXPECTED.items():
            with self.subTest(name=name):
                body = self.bodies[name]
                self.assertEqual(len(body), expected_size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)
                self.assertEqual(self.metadata[name]["alignment"], 2)
                self.assertEqual(self.metadata[name]["relocation_count"], 0)

    def test_source_preserves_void_eabi_and_independent_aligned_entry(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("exported as ISO C memcpy/memmove", text)
        self.assertIn("open_cfw_iar_memcpy_aligned_void", text)
        self.assertIn("push    {r4, r5}", text)
        self.assertIn("pop     {r4, r5}", text)

    def test_production_overlay_and_package_are_fail_closed(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {item["function"]: item for item in overlay["relocated_leaves"]}
        offsets = {
            "open_cfw_iar_memcpy_void": 130316,
            "open_cfw_iar_memcpy_aligned_void": 130468,
            "open_cfw_iar_memmove_void": 130620,
        }
        for name, offset in offsets.items():
            with self.subTest(name=name):
                self.assertEqual(leaves[name]["expected"]["offset"], offset)
                self.assertEqual(leaves[name]["relocations"], [])
                self.assertEqual(leaves[name]["source"]["size"], 6903)
                self.assertEqual(
                    leaves[name]["source"]["sha256"],
                    "3afa1466d5bd4d57a81d6b31debbb077eee1cecab029eebfbeff690a7658841d",
                )
                self.assertIn("linux-clang", leaves[name]["toolchain_profiles"])

        patches = {item["name"]: item for item in overlay["patch_sites"]}
        self.assertEqual(
            [
                (patches[name]["runtime_address"], patches[name]["expected_size"])
                for name in (
                    "replace_iar_memmove",
                    "replace_iar_memcpy_public",
                    "replace_iar_memcpy_aligned",
                )
            ],
            [(0x00439710, 150), (0x00439BE4, 32), (0x00439C04, 134)],
        )
        self.assertEqual(
            overlay["expected"],
            {
                "overlay_size": 147021,
                "overlay_sha256": "02c48ddcf4fa682ec14c3520ccac159c98a357aff4d18bd7e8ad01817e3bc2cd",
                "component_size": 3670417,
                "component_sha256": "eee145e7f687e622447bc33fc9dc45b3ab5eb1f1ad49717029196d589799aa4c",
            },
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            (4448911, "21ba9d6c32c73f390fd68ee9ef2808ad01c7206d746e67eca9c755732b0a6605"),
        )

    @unittest.skipUnless(
        os.environ.get("OPENCFW_RUN_UNICORN") == "1",
        "set OPENCFW_RUN_UNICORN=1 on a host with Python unicorn",
    )
    def test_target_bodies_against_randomized_oracles(self) -> None:
        result = subprocess.run(
            [sys.executable, str(EMULATOR), str(self.output), "--iterations", "2000"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("G2 IAR memory candidate emulation: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
