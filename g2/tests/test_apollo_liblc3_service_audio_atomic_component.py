#!/usr/bin/env python3
"""Exact and hostile checks for the joint CFF/LC3 component finalizer."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
BUILDER_PATH = COMPONENT / "build_service_audio_atomic_component.py"
MANIFEST = COMPONENT / "service_audio_atomic_component.json"
INPUTS = {
    "apple-clang": G2 / "build/canonical-observation/cff-apple/ota_s200_firmware_ota.bin",
    "linux-clang": G2 / "build/canonical-observation/cff-linux/ota_s200_firmware_ota.bin",
}


def load_builder():
    specification = importlib.util.spec_from_file_location(
        "open_cfw_test_liblc3_atomic_component", BUILDER_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load LC3 atomic component builder")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


BUILDER = load_builder()


class Lc3ServiceAudioAtomicComponentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-lc3-atomic-test-")
        cls.root = Path(cls.temporary.name)
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.reports = {}
        cls.outputs = {}
        for profile in ("apple-clang", "linux-clang"):
            output = cls.root / profile
            cls.reports[profile] = BUILDER.build(
                manifest_path=MANIFEST, input_component=INPUTS[profile],
                output_dir=output, profile=profile, record=False)
            cls.outputs[profile] = output / "ota_s200_firmware_ota.bin"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_profile_specific_receipts_and_inputs_are_exact(self) -> None:
        self.assertEqual(
            self.reports["apple-clang"]["input_component"]["sha256"],
            "aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2")
        self.assertEqual(
            self.reports["linux-clang"]["input_component"]["sha256"],
            "3255f998ea3c115803bf957e63b50e0b4a969cf478e64939610592c6fd4758f7")
        for profile, report in self.reports.items():
            self.assertEqual(
                BUILDER.canonical_sha256(report),
                self.manifest["profiles"][profile]["expected_report_sha256"])
            self.assertEqual(report["component"]["size"], 3956468)
            self.assertEqual(report["component"]["runtime_end_exclusive"],
                             0x007FDED4)
            self.assertEqual(report["component"]
                             ["protected_update_overlap_bytes"], 0)

    def test_apple_scatter_replays_suffix_and_preserves_cff(self) -> None:
        report = self.reports["apple-clang"]
        self.assertEqual((report["strict_suffix"]["leaf_count"],
                          report["strict_suffix"]["relocation_count"]),
                         (84, 288))
        artifacts = report["joint_finalization"]["artifacts"]
        self.assertEqual({name: (row["address"], row["size"])
                          for name, row in artifacts.items()}, {
            ".lc3_table_rodata": (0x007EA620, 404),
            ".rodata": (0x007EA7C0, 60480),
            ".lc3_scatter_0": (0x004580C4, 1972),
            ".lc3_scatter_1": (0x004D83DC, 1616),
            ".lc3_scatter_2": (0x00457A58, 1156),
            ".text": (0x007F9400, 14624),
        })
        self.assertEqual(artifacts[".text"]["address"] +
                         artifacts[".text"]["size"], 0x007FCD20)
        ingress = report["joint_layout"]["scatter_ingress"]
        self.assertTrue(ingress["all_entries_unreferenced"])
        self.assertTrue(ingress["all_branch_target_counts_zero"])
        self.assertTrue(
            ingress["all_aligned_word_pointer_target_counts_zero"])
        self.assertEqual([row["byte_window_pointer_target_count"]
                          for row in ingress["ranges"]], [0, 11, 2])
        self.assertEqual(report["joint_layout"]["forbidden_host_entries"]
                         ["forbidden_entry_count"], 115)

    def test_linux_uses_its_append_gap_without_apple_repack(self) -> None:
        report = self.reports["linux-clang"]
        self.assertEqual((report["strict_suffix"]["leaf_count"],
                          report["strict_suffix"]["relocation_count"]),
                         (0, 0))
        self.assertEqual(report["joint_layout"]["scatter_slots"], [])
        self.assertEqual(report["joint_layout"]["scatter_ingress"]["ranges"],
                         [])
        artifacts = report["joint_finalization"]["artifacts"]
        self.assertEqual({name: (row["address"], row["size"])
                          for name, row in artifacts.items()}, {
            ".lc3_table_rodata": (0x007BA050, 404),
            ".rodata": (0x007BA1F0, 60480),
            ".text": (0x007C8E30, 19308),
        })
        runtime = report["target_runtime"]["sections"]
        self.assertEqual(min(row["address"] for row in runtime), 0x007B9F10)
        self.assertLess(max(row["address"] + row["size"] for row in runtime),
                        artifacts[".lc3_table_rodata"]["address"])

    def test_all_relocations_tables_roots_and_unwind_policy_close(self) -> None:
        expected_relocations = {"apple-clang": 485, "linux-clang": 486}
        expected_cantunwind = {"apple-clang": 176, "linux-clang": 177}
        for profile, report in self.reports.items():
            final = report["joint_finalization"]
            self.assertEqual(final["input_relocations"],
                             expected_relocations[profile])
            self.assertEqual(final["output_relocations"], 0)
            self.assertEqual(final["undefined_symbols"], [])
            self.assertTrue(final["all_input_relocations_applied"])
            self.assertEqual((final["table_initializers"],
                              final["table_code_references"]), (78, 6))
            self.assertEqual(set(final["runtime_bindings"]), {
                "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf",
                "fmaxf", "fminf", "memcpy", "memmove", "memset",
                "sqrtf", "truncf",
            })
            self.assertEqual(final["roots"]
                             ["open_cfw_liblc3_service_audio_stock_encode"]
                             ["size"], 224)
            self.assertEqual(final["roots"]
                             ["open_cfw_liblc3_service_audio_stock_setup"]
                             ["size"], 96)
            compile_report = report["lc3_compile"]
            self.assertEqual(
                compile_report["canonical_cantunwind_rows_discarded"],
                expected_cantunwind[profile])
            self.assertEqual(compile_report["retained_unwind_sections"], 0)
            self.assertEqual(report["component"]["adapter_state"], {
                "contexts": [0x20106A7C, 0x201074C0,
                             0x20107F04, 0x20108948],
                "slot_count": 4, "slot_bytes": 2628,
                "total_bytes": 10512, "end_exclusive": 0x2010938C,
                "flash_initializer_bytes": 0,
            })

    def test_cff_bytes_header_crc_and_update_boundary_are_preserved(self) -> None:
        for profile, report in self.reports.items():
            before = INPUTS[profile].read_bytes()
            after = self.outputs[profile].read_bytes()
            for row in report["joint_layout"]["cff_intervals"]:
                first = 32 + row["start"] - 0x00438000
                last = 32 + row["end_exclusive"] - 0x00438000
                self.assertEqual(after[first:last], before[first:last],
                                 row["owner"])
            self.assertEqual(struct.unpack_from("<I", after, 0)[0],
                             0x04000000 | len(after))
            self.assertEqual(struct.unpack_from("<I", after, 4)[0],
                             zlib.crc32(after[8:]) & 0xFFFFFFFF)
            self.assertTrue(report["joint_layout"]["zero_overlap_verified"])
            self.assertEqual(report["joint_layout"]
                             ["protected_update_start"], 0x007FE000)
            self.assertEqual(report["joint_layout"]
                             ["protected_update_overlap_bytes"], 0)

    def test_second_dual_profile_build_is_byte_identical(self) -> None:
        for profile in ("apple-clang", "linux-clang"):
            output = self.root / f"{profile}-second"
            second = BUILDER.build(
                manifest_path=MANIFEST, input_component=INPUTS[profile],
                output_dir=output, profile=profile, record=False)
            self.assertEqual(second, self.reports[profile])
            self.assertEqual(
                (output / "build-report.json").read_bytes(),
                (self.root / profile / "build-report.json").read_bytes())
            self.assertEqual(
                (output / "ota_s200_firmware_ota.bin").read_bytes(),
                self.outputs[profile].read_bytes())

    def test_hostile_profile_scatter_overlap_and_pin_drift_fail_closed(self) -> None:
        with self.assertRaisesRegex(BUILDER.AtomicComponentError,
                                    "input CFF component pin drift"):
            BUILDER.build(
                manifest_path=MANIFEST,
                input_component=INPUTS["apple-clang"],
                output_dir=self.root / "crossed-profile",
                profile="linux-clang", record=False)

        mutated = copy.deepcopy(self.manifest)
        mutated["builder"]["sha256"] = "0" * 64
        hostile = self.root / "hostile-builder.json"
        hostile.write_text(json.dumps(mutated), encoding="utf-8")
        with self.assertRaisesRegex(BUILDER.AtomicComponentError,
                                    "source pin drift"):
            BUILDER.build(
                manifest_path=hostile,
                input_component=INPUTS["apple-clang"],
                output_dir=self.root / "builder-pin-drift",
                profile="apple-clang", record=False)

        apple = self.reports["apple-clang"]
        placements = {
            ".text.fft": 0x00457A58,
            ".text.lc3_sns_analyze": 0x004580C4,
            ".text.lc3_tns_analyze": 0x004D83DC,
        }
        with self.assertRaisesRegex(BUILDER.AtomicComponentError,
                                    "scatter ingress receipt drift"):
            BUILDER._scatter_ingress(
                INPUTS["apple-clang"].read_bytes(), placements,
                apple["lc3_compile"]["text_inputs"], [])
        with self.assertRaisesRegex(BUILDER.AtomicComponentError,
                                    "joint output intervals overlap"):
            BUILDER._intervals_disjoint([
                (0x1000, 0x1100, "left"),
                (0x10FF, 0x1200, "right"),
            ])
        with self.assertRaisesRegex(BUILDER.AtomicComponentError,
                                    "address outside application"):
            BUILDER.image_write(bytearray(64), 0x007FE000, b"")

    def test_package_and_hardware_authority_remain_fail_closed(self) -> None:
        for report in self.reports.values():
            self.assertEqual(report["routing"], {
                "component_mutations_applied_atomically": True,
                "service_audio_veneers_applied": True,
                "component_crc_repaired": True,
                "outer_evenota_package_emitted": False,
                "hardware_operations": False,
                "hardware_qualified": False,
            })
            self.assertEqual(len(report["remaining_software_blockers"]), 1)


if __name__ == "__main__":
    unittest.main()
