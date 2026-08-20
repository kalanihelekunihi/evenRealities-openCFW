#!/usr/bin/env python3
"""Static and optional differential qualification for IAR exponent helpers."""

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
SOURCE = (
    ROOT
    / "components/apollo_main/core_overlay/candidates/iar_runtime_float_exponent.S"
)
EMULATOR = ROOT / "tools/emulate_g2_iar_float_exponent.py"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
LOAD_ADDRESS = 0x00437FE0
EXPECTED = {
    "open_cfw_iar_frexpf": (
        20,
        "7e039dc3fe4997dab68e5a3d8d04686f11b41dac00645548ed9921db219f433c",
    ),
    "open_cfw_iar_frexpf_bits": (
        52,
        "77a18771325e8acc19148f0ed42f562aa5c4b5a948f4720de1e93883723a60b4",
    ),
    "open_cfw_iar_ldexpf": (
        196,
        "41ebd370051b6e19d498c686248356f8d35a285f191ad210773e76f7cbad3ae9",
    ),
}
STOCK = {
    "open_cfw_iar_frexpf": (
        0x0059D244,
        "420aee8c563327dfd7e8b3e1acefd07f473cbe3917f09854c45285866f60a487",
    ),
    "open_cfw_iar_frexpf_bits": (
        0x0059D258,
        "77a18771325e8acc19148f0ed42f562aa5c4b5a948f4720de1e93883723a60b4",
    ),
    "open_cfw_iar_ldexpf": (
        0x0059D28C,
        "314f08b4ed19f0ad2b7afdcdec50da41f1ba983725a3198d813051b31fed93fb",
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


class IARRuntimeFloatExponentCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.temporary = tempfile.TemporaryDirectory(prefix="openCFW-iar-float-exp-")
        cls.output = Path(cls.temporary.name)
        compiler = subprocess.run(
            ["xcrun", "-f", "clang"], check=True, capture_output=True, text=True
        ).stdout.strip()
        cls.bodies: dict[str, bytes] = {}
        cls.metadata: dict[str, dict[str, int | str]] = {}
        for selection, name in enumerate(EXPECTED):
            object_path = cls.output / f"{selection}.o"
            subprocess.run(
                [
                    compiler,
                    *TARGET_FLAGS,
                    f"-DOPEN_CFW_IAR_FLOAT_EXPONENT_SELECTION={selection}",
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
            body = data[start : start + int(section["size"])]
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

    def test_relocated_bodies_reproduce_authenticated_stock_exactly(self) -> None:
        image = IMAGE.read_bytes()
        for name, (stock_address, stock_hash) in STOCK.items():
            body = bytearray(self.bodies[name])
            if name == "open_cfw_iar_frexpf":
                body[8:12] = self.apollo_overlay.encode_thumb_bl(
                    stock_address + 8, STOCK["open_cfw_iar_frexpf_bits"][0]
                )
            elif name == "open_cfw_iar_ldexpf":
                body[190:194] = self.apollo_overlay.encode_thumb_b_w(
                    stock_address + 190, 0x00439CB2
                )
            start = stock_address - LOAD_ADDRESS
            stock = image[start : start + len(body)]
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256(stock).hexdigest(), stock_hash)
                self.assertEqual(bytes(body), stock)

    def test_source_preserves_recovered_hard_float_contract(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("vmov    r0, s0", text)
        self.assertIn("vmov    s0, r0", text)
        self.assertIn("vmul.f32 s0, s0, s1", text)
        self.assertIn("vmrs    r1, fpscr", text)
        self.assertIn("vmsr    fpscr, r1", text)
        self.assertIn("open_cfw_iar_range_error", text)

    def test_canonical_overlay_and_package_are_fail_closed(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {item["function"]: item for item in overlay["relocated_leaves"]}
        expected = {
            "open_cfw_iar_frexpf_bits": (52, 142310, []),
            "open_cfw_iar_frexpf": (
                20,
                142362,
                [
                    {
                        "offset": 8,
                        "type": "R_ARM_THM_CALL",
                        "symbol": "open_cfw_iar_frexpf_bits",
                        "symbol_type": "STT_NOTYPE",
                        "target_function": "open_cfw_iar_frexpf_bits",
                    }
                ],
            ),
            "open_cfw_iar_ldexpf": (
                196,
                142382,
                [
                    {
                        "offset": 190,
                        "type": "R_ARM_THM_JUMP24",
                        "symbol": "open_cfw_iar_range_error",
                        "symbol_type": "STT_NOTYPE",
                        "target_function": "open_cfw_iar_range_error",
                    }
                ],
            ),
        }
        for name, (size, offset, relocations) in expected.items():
            with self.subTest(name=name):
                leaf = leaves[name]
                self.assertEqual(leaf["profiles"], ["apple-clang"])
                self.assertEqual((leaf["expected"]["size"], leaf["expected"]["offset"]), (size, offset))
                self.assertEqual(leaf["relocations"], relocations)
                self.assertEqual(leaf["source"]["size"], 4022)
                self.assertEqual(
                    leaf["source"]["sha256"],
                    "3189bb3a834e8a95caff6a004ee0ab10f7541f5c2af17f715606526ca5aa51a9",
                )

        patches = {item["name"]: item for item in overlay["patch_sites"]}
        self.assertEqual(
            [
                (patches[name]["runtime_address"], patches[name]["expected_size"])
                for name in (
                    "replace_iar_frexpf",
                    "replace_iar_frexpf_bits",
                    "replace_iar_ldexpf",
                )
            ],
            [(0x0059D244, 20), (0x0059D258, 52), (0x0059D28C, 196)],
        )
        self.assertTrue(
            all(
                patches[name]["profiles"] == ["apple-clang"]
                for name in (
                    "replace_iar_frexpf",
                    "replace_iar_frexpf_bits",
                    "replace_iar_ldexpf",
                )
            )
        )
        self.assertEqual(
            overlay["expected"],
            {
                "overlay_size": 164536,
                "overlay_sha256": "a437e33ec76c3531ecb2b66d7239229b3a1d905bdc76b00cb564bd05b7ac2546",
                "component_size": 3687932,
                "component_sha256": "4fdb5af59a3ae68ce25c2d3255fcc4f4ea0c9a77f2ac89a1d16532496c082c07",
            },
        )
        filtered = self.apollo_overlay.filter_config_for_profile(overlay, "linux-clang")
        self.assertFalse(
            {"open_cfw_iar_frexpf", "open_cfw_iar_frexpf_bits", "open_cfw_iar_ldexpf"}
            & set(filtered["functions"])
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            (4466426, "cc1642fdf85d2af71ba4c3c40335fe4e8b431eb5f578d501b1b260f43fcdd3f4"),
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
        self.assertIn("'frexpf': 2000", result.stdout)
        self.assertIn("'ldexpf': 2000", result.stdout)


if __name__ == "__main__":
    unittest.main()
