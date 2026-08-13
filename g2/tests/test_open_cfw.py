from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import open_cfw  # noqa: E402


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

    def test_corrupted_main_is_rejected(self) -> None:
        corrupted = bytearray(self.payloads["apollo_main"])
        corrupted[-1] ^= 0x01
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "nested CRC-32"):
            open_cfw.validate_apollo_main(bytes(corrupted))

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


if __name__ == "__main__":
    unittest.main()
