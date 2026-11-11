from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import open_cfw  # noqa: E402

from tests.official_payloads import require as _require_official

_require_official('ota_s200_firmware_ota.bin', 'ota_s200_bootloader.bin', 'firmware_codec.bin', 'firmware_ble_em9305.bin', 'firmware_touch.bin', 'firmware_box.bin')


MANIFEST_PATH = OPENCFW_ROOT / "manifests" / "g2-2.2.6.10.json"


class OpenCFWTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest, cls.project_root, cls.payloads = open_cfw.verify_manifest(
            MANIFEST_PATH
        )
        cls.image, cls.entries = open_cfw.assemble_evenota(
            cls.manifest,
            cls.payloads,
        )

    def test_reassembles_pinned_reference_exactly(self) -> None:
        package = self.manifest["package"]
        self.assertEqual(len(self.image), package["expected_size"])
        self.assertEqual(
            hashlib.sha256(self.image).hexdigest(),
            package["expected_sha256"],
        )
        self.assertEqual([entry.type_id for entry in self.entries], [4, 5, 3, 6, 1, 0])

    def test_all_component_regions_form_exact_partitions(self) -> None:
        for component in self.manifest["components"]:
            data = self.payloads[component["name"]]
            open_cfw.validate_region_partition(component, data)
            reconstructed = b"".join(
                data[region["file_offset"]:region["file_offset"] + region["size"]]
                for region in component["regions"]
            )
            self.assertEqual(reconstructed, data)

    def test_native_wrappers_reproduce_official_payloads(self) -> None:
        main = self.payloads["apollo_main"]
        case = self.payloads["case"]
        touch = self.payloads["touch"]
        self.assertEqual(open_cfw.wrap_main_image(main[0x20:]), main)
        self.assertEqual(open_cfw.wrap_case_image(case[0x20:]), case)
        self.assertEqual(open_cfw.wrap_touch_image(touch[0x20:]), touch)

    def test_touch_wrapper_uses_application_flash_base(self) -> None:
        # The source image starts at 0x3300; a valid reset vector may exceed
        # the image's byte length when interpreted from address zero.
        raw = bytearray(0x100)
        raw[0:4] = (0x20002000).to_bytes(4, "little")
        raw[4:8] = (0x3301).to_bytes(4, "little")
        wrapped = open_cfw.wrap_touch_source_image(bytes(raw))
        open_cfw.validate_touch(wrapped)
        self.assertEqual(len(wrapped), len(raw) + 36)
        corrupted = bytearray(wrapped)
        corrupted[-1] ^= 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "CRC-32C"):
            open_cfw.validate_touch(bytes(corrupted))
        raw[4:8] = (0x3201).to_bytes(4, "little")
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "outside the image"):
            open_cfw.wrap_touch_source_image(bytes(raw))

    def test_codec_uart_boot_header_reproduces_stock_segment(self) -> None:
        codec = self.payloads["codec"]
        segment = codec[0x30:0x30 + 38236]
        stage1 = segment[32:32 + 0x2800]
        stage2 = segment[32 + 0x2800:]
        self.assertEqual(open_cfw.wrap_codec_uart_boot(stage1, stage2), segment)
        invalid = bytearray(stage2)
        invalid[0] ^= 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "vectors"):
            open_cfw.wrap_codec_uart_boot(stage1, bytes(invalid))

    def test_codec_binh_b_wrap_reproduces_stock_image(self) -> None:
        codec = self.payloads["codec"]
        image = codec[0x958C + 0x2F3B0:0x958C + 0x46440]
        stage1 = image[24:0x3000 - 4]
        stage2 = image[0x3004:]
        self.assertEqual(open_cfw.wrap_codec_binh_b(stage1, stage2), image)
        invalid = bytearray(stage1)
        invalid[0] ^= 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "stage-1 vectors"):
            open_cfw.wrap_codec_binh_b(bytes(invalid), stage2)

    def test_codec_binh_a_and_fwpk_wrap_reproduce_stock(self) -> None:
        codec = self.payloads["codec"]
        uart = codec[0x30:0x958C]
        flash = codec[0x958C:]
        image_a = flash[:0x2F3B0]
        image_b = flash[0x2F3B0:]
        stage1 = image_a[24:0x3000 - 4]
        xip = image_a[0x3004:0xBE88]
        sram = image_a[0xBE88:0xF804]
        commands = image_a[0xF804:0x11BD0]
        weights = image_a[0x11BD0:]
        self.assertEqual(open_cfw.wrap_codec_binh_a(
            stage1, xip, sram, commands, weights), image_a)
        self.assertEqual(open_cfw.wrap_codec_fwpk(uart, image_a, image_b), codec)
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "XIP load size"):
            open_cfw.wrap_codec_binh_a(stage1, xip + b"\0", sram,
                                      commands, weights)
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "NPU source regions"):
            open_cfw.wrap_codec_binh_a(stage1, xip, sram,
                                      commands[:-1], weights)

    def test_corrupted_main_is_rejected(self) -> None:
        corrupted = bytearray(self.payloads["apollo_main"])
        corrupted[-1] ^= 0x01
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "nested CRC-32"):
            open_cfw.validate_apollo_main(bytes(corrupted))

    def test_manifest_must_decode_to_an_object(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = Path(temporary) / "manifest.json"
            manifest.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(
                open_cfw.OpenCFWError, "must contain a JSON object"
            ):
                open_cfw.load_manifest(manifest)

    def test_provider_must_be_a_regular_nonsymlink_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            provider = root / "provider.bin"
            target = root / "target.bin"
            target.write_bytes(b"provider")
            provider.symlink_to(target.name)
            manifest = {
                "components": [
                    {
                        "name": "test_component",
                        "entry_id": 1,
                        "provider": {
                            "kind": "official_blob",
                            "path": "provider.bin",
                            "size": len(target.read_bytes()),
                            "sha256": open_cfw.sha256_bytes(target.read_bytes()),
                        },
                    }
                ]
            }
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "symlink"):
                open_cfw.read_providers(manifest, root)
            provider.unlink()
            provider.mkdir()
            with self.assertRaisesRegex(open_cfw.OpenCFWError, "not a regular file"):
                open_cfw.read_providers(manifest, root)

    def test_build_emits_addressed_plan_and_unresolved_codec(self) -> None:
        build_parent = OPENCFW_ROOT / "build"
        build_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=build_parent) as temp:
            output = Path(temp)
            report = open_cfw.build(MANIFEST_PATH, output)
            plan = json.loads((output / "flash-plan.json").read_text())
            self.assertTrue(report["package"]["byte_identical_to_reference"])
            addresses = {
                region["target_address_hex"]
                for region in plan["flash_regions"]
            }
            self.assertIn("0x00438000", addresses)
            self.assertIn("0x08000000", addresses)
            self.assertIn("0x00302400", addresses)
            self.assertEqual(
                {
                    region["region"]
                    for region in plan["unresolved_flash_regions"]
                },
                {"codec_stage_1", "codec_stage_2"},
            )
            semantics = plan["address_status_semantics"]
            self.assertEqual(
                semantics["ownership_labels"],
                "authoritative_provider_origin_only",
            )
            self.assertIsNone(
                semantics["authoritative_ownership_companion"]
            )
            self.assertEqual(semantics["typed_mixed_profile_spans"], [])


if __name__ == "__main__":
    unittest.main()
