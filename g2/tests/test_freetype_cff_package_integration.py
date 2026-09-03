# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER_PATH = G2 / "tools/analyze_g2_freetype_cff_package_integration.py"


def load(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


class FreeTypeCffPackageIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load(ANALYZER_PATH, "test_cff_package_integration")
        cls.builder = load(cls.analyzer.BUILDER, "test_cff_package_builder")
        cls.open_cfw = load(cls.analyzer.OPEN_CFW, "test_cff_package_open_cfw")
        cls.report = cls.analyzer.analyze()
        cls.config = json.loads(cls.analyzer.CONFIG.read_text(encoding="utf-8"))

    def test_checked_manifest_matches_deterministic_analysis(self) -> None:
        checked = json.loads(self.analyzer.MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.report)
        self.assertEqual(
            self.report["integration_sha256"],
            "52b2c8c6764e760df691d248a8673ef41b095be1b4f29111c816f085eee7e0f1",
        )

    def test_dual_profile_package_receipts_are_exact(self) -> None:
        expected = {
            "apple-clang": (
                3_956_672,
                "7e7456eddfc5832bd0dd8522706c4b95bcc9ab3ab66d71f56728f8395e6f88fe",
                4_750_780,
                "f2842600b84f303c40d2d299761c1abc0a7083acc05f2d378be9a045b0d9a846",
                "0x327A621C",
                "0x005AFEB8",
            ),
            "linux-clang": (
                3_956_672,
                "64f6e109a83331ef31c9c7245ef05458779f1031f514ad12a228b2aacb09fa38",
                4_750_764,
                "e534ffe034360b24fffc3d7fc50988234fc48ae20f6e8afa8be2507247c8cd39",
                "0xDD72C07D",
                "0x005AFE7C",
            ),
        }
        for profile, values in expected.items():
            (component_size, component_sha, package_size, package_sha, crc,
             highest) = values
            row = self.report["profiles"][profile]
            self.assertEqual((row["component"]["size"], row["component"]["sha256"]),
                             (component_size, component_sha))
            self.assertEqual((row["package"]["size"], row["package"]["sha256"],
                              row["package"]["entry_6_crc32c_msb"]),
                             (package_size, package_sha, crc))
            self.assertEqual(row["ownership"]["highest_cff_end_exclusive"],
                             highest)
            self.assertEqual(row["ownership"]["collision_or_protected_overlap_count"], 0)
            self.assertEqual(row["ownership"]["unused_scattered_table_pool_consumed"], 0)

    def test_component_output_revalidates_guards_crc_padding_and_sections(self) -> None:
        profile = "apple-clang"
        component_path = (
            G2 / self.config["profiles"][profile]["base_component"]["path"]
        )
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "candidate"
            report = self.builder.build(
                profile=profile, base_component=component_path,
                output_dir=output,
                host_slots=self.analyzer.HOST_SLOTS[profile],
            )
            component = (output / "ota_s200_firmware_ota.bin").read_bytes()
            self.open_cfw.validate_apollo_main(component)
            self.assertEqual(struct.unpack_from("<I", component, 0)[0] & 0xFFFFFF,
                             len(component))
            self.assertEqual(struct.unpack_from("<I", component, 4)[0],
                             zlib.crc32(component[8:]) & 0xFFFFFFFF)
            slot = self.builder._runtime_offset(self.builder.MODULE_SLOT)
            self.assertEqual(component[slot:slot + 4],
                             self.builder.REPLACEMENT_CLASS_BYTES)
            self.assertTrue(report["placement"]["host_scatter"])
            self.assertGreater(report["placement"]["host_slot_count"], 0)
            for section in report["placement"]["sections"]:
                start = self.builder._runtime_offset(section["start"])
                artifact = output / f"{section['name'][1:]}.bin"
                body = artifact.read_bytes()
                self.assertEqual(component[start:start + len(body)], body)

    def _mutated_component_and_config(
        self, profile: str, address: int
    ) -> tuple[Path, dict]:
        component_path = (
            G2 / self.config["profiles"][profile]["base_component"]["path"]
        )
        component = bytearray(component_path.read_bytes())
        component[self.builder._runtime_offset(address)] ^= 0x01
        struct.pack_into("<I", component, 4, zlib.crc32(component[8:]) & 0xFFFFFFFF)
        config = copy.deepcopy(self.config)
        expected = config["profiles"][profile]
        expected["base_component"].update({
            "size": len(component), "sha256": self.builder.digest(bytes(component))
        })
        temporary = tempfile.NamedTemporaryFile(delete=False)
        temporary.write(component)
        temporary.close()
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        return Path(temporary.name), config

    def test_hostile_stock_interval_mutation_is_rejected_after_valid_crcs(self) -> None:
        path, config = self._mutated_component_and_config(
            "apple-clang", self.builder.STOCK_INTERVAL[0]
        )
        with self.assertRaisesRegex(self.builder.BuildError, "stock CFF interval guard"):
            self.builder._authenticate_component(path, "apple-clang", config)

    def test_hostile_class_pointer_mutation_is_rejected_after_valid_crcs(self) -> None:
        path, config = self._mutated_component_and_config(
            "linux-clang", self.builder.MODULE_SLOT
        )
        with self.assertRaisesRegex(self.builder.BuildError, "class-pointer guard"):
            self.builder._authenticate_component(path, "linux-clang", config)

    def test_hostile_dependency_pin_and_tail_collision_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "overlay.json"
            body = bytearray(self.analyzer.CONFIG.read_bytes())
            body[-2] ^= 1
            path.write_bytes(body)
            with self.assertRaisesRegex(
                self.analyzer.IntegrationError, "input pin drift"
            ):
                self.analyzer._pin_inputs({self.analyzer.CONFIG: path})
        config = copy.deepcopy(self.config)
        profile = config["profiles"]["apple-clang"]
        profile["base_component"]["runtime_end_exclusive"] = self.builder.TAIL_TEXT_START + 4
        component = G2 / profile["base_component"]["path"]
        with self.assertRaisesRegex(self.builder.BuildError, "runtime end drift"):
            self.builder._authenticate_component(component, "apple-clang", config)

    def test_canonical_manifest_and_package_route_are_published(self) -> None:
        self.assertEqual(self.report["routing"], {
            "component_builder_integration_present": True,
            "canonical_component_route_enabled": True,
            "dual_profile_package_candidate_emitted_in_verification": True,
            "canonical_package_manifest_route_enabled": True,
            "software_production_route_permitted": True,
            "hardware_validation_performed": False,
        })
        self.assertEqual(self.report["remaining_canonical_changes"], [])


if __name__ == "__main__":
    unittest.main()
