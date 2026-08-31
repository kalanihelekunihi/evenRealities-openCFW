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
            "d9c8cf3c9a05af35922ae3e1b06eb14dc36ae59ba9005b7e83b20316c7f544e1",
        )

    def test_dual_profile_package_receipts_are_exact(self) -> None:
        expected = {
            "apple-clang": (
                3_956_468,
                "aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2",
                4_749_540,
                "482756200d1b3c70685d7c1c29c422a5725436801e3600d7cf55fa3e16809128",
                "0x0012B7B8",
            ),
            "linux-clang": (
                3_956_468,
                "3255f998ea3c115803bf957e63b50e0b4a969cf478e64939610592c6fd4758f7",
                4_749_524,
                "d9386d30c0c6b1bd706b36c9ee095ad6e2e9ee9b5dacf9c58a52357c7620a362",
                "0xD90D86A3",
            ),
        }
        for profile, values in expected.items():
            component_size, component_sha, package_size, package_sha, crc = values
            row = self.report["profiles"][profile]
            self.assertEqual((row["component"]["size"], row["component"]["sha256"]),
                             (component_size, component_sha))
            self.assertEqual((row["package"]["size"], row["package"]["sha256"],
                              row["package"]["entry_6_crc32c_msb"]),
                             (package_size, package_sha, crc))
            self.assertEqual(row["ownership"]["highest_cff_end_exclusive"],
                             "0x007FDED4")
            self.assertEqual(row["ownership"]["collision_or_protected_overlap_count"], 0)
            self.assertEqual(row["ownership"]["unused_scattered_table_pool_consumed"], 0)

    def test_component_output_revalidates_guards_crc_padding_and_sections(self) -> None:
        profile = "apple-clang"
        package = G2 / self.config["profiles"][profile]["base_package"]["path"]
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "candidate"
            report = self.builder.build(
                profile=profile, base_package=package, output_dir=output
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
            gap_start = self.builder._runtime_offset(
                int(report["placement"]["erased_gap_start"], 16)
            )
            gap_end = self.builder._runtime_offset(self.builder.TAIL_TEXT_START)
            self.assertEqual(set(component[gap_start:gap_end]), {0xFF})
            for section in report["placement"]["sections"]:
                start = self.builder._runtime_offset(section["start"])
                artifact = output / f"{section['name'][1:]}.bin"
                body = artifact.read_bytes()
                self.assertEqual(component[start:start + len(body)], body)

    def _mutated_package_and_config(self, profile: str, address: int) -> tuple[Path, dict]:
        package_path = G2 / self.config["profiles"][profile]["base_package"]["path"]
        package = bytearray(package_path.read_bytes())
        count = struct.unpack_from("<I", package, 8)[0]
        index = next(i for i in range(count)
                     if struct.unpack_from("<I", package, 0x40 + i * 16)[0] == 6)
        toc = 0x40 + index * 16
        offset, size = struct.unpack_from("<II", package, toc + 4)
        component = bytearray(package[offset + 128:offset + size])
        component[self.builder._runtime_offset(address)] ^= 0x01
        struct.pack_into("<I", component, 4, zlib.crc32(component[8:]) & 0xFFFFFFFF)
        package[offset + 128:offset + size] = component
        crc = self.open_cfw.crc32c_msb(component)
        struct.pack_into("<I", package, toc + 12, crc)
        struct.pack_into("<I", package, offset + 12, crc)
        config = copy.deepcopy(self.config)
        expected = config["profiles"][profile]
        expected["base_package"].update({
            "size": len(package), "sha256": self.builder.digest(bytes(package))
        })
        expected["base_component"].update({
            "size": len(component), "sha256": self.builder.digest(bytes(component))
        })
        temporary = tempfile.NamedTemporaryFile(delete=False)
        temporary.write(package)
        temporary.close()
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        return Path(temporary.name), config

    def test_hostile_stock_interval_mutation_is_rejected_after_valid_crcs(self) -> None:
        path, config = self._mutated_package_and_config(
            "apple-clang", self.builder.STOCK_INTERVAL[0]
        )
        with self.assertRaisesRegex(self.builder.BuildError, "stock CFF interval guard"):
            self.builder._authenticate_base(path, "apple-clang", config)

    def test_hostile_class_pointer_mutation_is_rejected_after_valid_crcs(self) -> None:
        path, config = self._mutated_package_and_config(
            "linux-clang", self.builder.MODULE_SLOT
        )
        with self.assertRaisesRegex(self.builder.BuildError, "class-pointer guard"):
            self.builder._authenticate_base(path, "linux-clang", config)

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
        package = G2 / profile["base_package"]["path"]
        with self.assertRaisesRegex(self.builder.BuildError, "runtime end drift"):
            self.builder._authenticate_base(package, "apple-clang", config)

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
