#!/usr/bin/env python3
"""Static qualification for the clean-room IAR math/errno candidates."""

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
SOURCE = ROOT / "components/apollo_main/core_overlay/candidates/iar_runtime_math_errno.S"
EMULATOR = ROOT / "tools/emulate_g2_iar_math_errno.py"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
EXPECTED = {
    "open_cfw_iar_sqrtf": (
        28,
        "7fb8c75c9889a4c4d92014218c546be5744eb7bdadaf2f4f5382691c1dd8e888",
    ),
    "open_cfw_iar_domain_error": (
        20,
        "a95dc7521a542f97ed53f483e6aa2889d22e128799535f979dfe742f447ed16d",
    ),
    "open_cfw_iar_range_error": (
        20,
        "83e8d326849245389ee02362fd8694d7eedcba34b8ea6330dbdf7ab92048a518",
    ),
    "open_cfw_iar_errno_address": (
        10,
        "86dcc309589b8b5348ab0c836b92cb168f22d3914daf11800ae21fe92e1e8f1b",
    ),
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


class IARRuntimeMathErrnoCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.temporary = tempfile.TemporaryDirectory(prefix="openCFW-iar-math-errno-")
        cls.output = Path(cls.temporary.name)
        compiler = subprocess.run(
            ["xcrun", "-f", "clang"], check=True, capture_output=True, text=True
        ).stdout.strip()
        cls.bodies = {}
        cls.metadata = {}
        for selection, name in enumerate(EXPECTED):
            object_path = cls.output / f"{selection}.o"
            subprocess.run(
                [
                    compiler,
                    *TARGET_FLAGS,
                    f"-DOPEN_CFW_IAR_MATH_ERRNO_SELECTION={selection}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(object_path),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            data, sections = apollo_overlay.parse_elf32(object_path)
            section = apollo_overlay.section_named(sections, f".text.{name}")
            start = int(section["offset"])
            body = data[start:start + int(section["size"])]
            cls.bodies[name] = body
            cls.metadata[name] = {
                "alignment": int(section["alignment"]),
                "sha256": hashlib.sha256(body).hexdigest(),
            }
            (cls.output / f"{name}.bin").write_bytes(body)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_sections_are_selector_isolated_and_byte_pinned(self) -> None:
        for name, (expected_size, expected_hash) in EXPECTED.items():
            with self.subTest(name=name):
                self.assertEqual(len(self.bodies[name]), expected_size)
                self.assertEqual(self.metadata[name]["sha256"], expected_hash)
                self.assertEqual(self.metadata[name]["alignment"], 2)

    def test_source_preserves_recovered_abi_contract(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("vcmpe.f32 s0, #0", text)
        self.assertIn("vsqrt.f32 s0, s0", text)
        self.assertIn("open_cfw_iar_domain_error", text)
        self.assertIn("movw    r1, #0x4f14", text)
        self.assertIn("movt    r1, #0x2007", text)
        self.assertIn("OPEN_CFW_SET_ERRNO 33", text)
        self.assertIn("OPEN_CFW_SET_ERRNO 34", text)

    def test_production_overlay_and_package_are_fail_closed(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {item["function"]: item for item in overlay["relocated_leaves"]}
        offsets = {
            "open_cfw_iar_domain_error": (190790, 192562),
            "open_cfw_iar_sqrtf": (190810, 192582),
            "open_cfw_iar_range_error": (190838, 192610),
            "open_cfw_iar_errno_address": (190858, 192630),
        }
        for name, (apple_offset, linux_offset) in offsets.items():
            with self.subTest(name=name):
                leaf = leaves[name]
                self.assertEqual(leaf["expected"]["offset"], apple_offset)
                self.assertEqual(
                    leaf["toolchain_profiles"]["linux-clang"]["expected"]["offset"],
                    linux_offset,
                )
                self.assertEqual(leaf["source"]["size"], 2625)
                self.assertEqual(
                    leaf["source"]["sha256"],
                    "b5288643766f14f62a2452f445f58e0e3ec8e09c229f4f9c572b8dd1c5c0f59c",
                )

        self.assertEqual(
            leaves["open_cfw_iar_sqrtf"]["relocations"],
            [
                {
                    "offset": 24,
                    "type": "R_ARM_THM_JUMP24",
                    "symbol": "open_cfw_iar_domain_error",
                    "symbol_type": "STT_NOTYPE",
                    "target_function": "open_cfw_iar_domain_error",
                }
            ],
        )
        patches = {item["name"]: item for item in overlay["patch_sites"]}
        self.assertEqual(
            [
                (patches[name]["runtime_address"], patches[name]["expected_size"])
                for name in (
                    "replace_iar_sqrtf",
                    "replace_iar_domain_error",
                    "replace_iar_range_error",
                    "replace_iar_errno_address",
                )
            ],
            [(0x004397A8, 28), (0x00439CA4, 14), (0x00439CB2, 18), (0x00439CC4, 12)],
        )
        self.assertEqual(
            overlay["expected"],
            {
                "overlay_size": 429058,
                "overlay_sha256": "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd",
                "component_size": 3952454,
                "component_sha256": "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb",
            },
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            (4745526, "4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934"),
        )
        self.assertEqual(
            (
                manifest["package"]["profiles"]["linux-clang"]["expected_size"],
                manifest["package"]["profiles"]["linux-clang"]["expected_sha256"],
            ),
            (4529116, "f0526433c366a85ab79e27df6d28ffc70d6a2ed93e608652885b49b404e380ef"),
        )

    @unittest.skipUnless(
        os.environ.get("OPENCFW_RUN_UNICORN") == "1",
        "set OPENCFW_RUN_UNICORN=1 on a host with Python unicorn",
    )
    def test_target_bodies_against_authenticated_stock(self) -> None:
        result = subprocess.run(
            [sys.executable, str(EMULATOR), str(self.output), "--iterations", "2000"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("G2 IAR math/errno candidate emulation: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
