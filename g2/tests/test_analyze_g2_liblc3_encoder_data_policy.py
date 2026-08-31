"""Hostile tests for the specialized LC3 immutable-XIP data policy."""

from __future__ import annotations

import copy
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER_PATH = ROOT / "tools/analyze_g2_liblc3_encoder_data_policy.py"
SPEC = importlib.util.spec_from_file_location(
    "analyze_g2_liblc3_encoder_data_policy", ANALYZER_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


class Liblc3EncoderDataPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = ANALYZER.run_audit()
        cls.manifest = json.loads(
            ANALYZER.MANIFEST.read_text(encoding="utf-8"))
        cls.initialization = cls.manifest["expected"]["common_initialization"]

    def template(self) -> bytes:
        payload = bytearray(ANALYZER.TABLE_BYTES)
        for index, offset in enumerate(
                self.initialization["relocation_offsets"]):
            struct.pack_into("<I", payload, offset, 4 * (index + 1))
        return bytes(payload)

    def test_exact_table_objects_and_profile_geometry(self) -> None:
        self.assertEqual(self.report["baseline"], {
            "specialized_data_size": 404,
            "specialized_data_sha256":
                "c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a",
            "specialized_data_relocations": 78,
        })
        expected_symbols = {
            name: {"offset": offset, "size": size}
            for name, (offset, size) in ANALYZER.TABLE_SYMBOLS.items()
        }
        for profile, receipt in self.report["profiles"].items():
            with self.subTest(profile=profile):
                self.assertEqual(receipt["table_symbols"], expected_symbols)
                self.assertEqual(receipt["sections"]["table_rodata"], {
                    "size": 404,
                    "alignment": 8,
                    "flags": ["SHF_ALLOC"],
                    "sha256":
                        "c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a",
                })
                self.assertEqual(
                    receipt["post_policy_object"]["allocated_writable_sections"],
                    [])
                self.assertEqual(
                    set(receipt["post_policy_object"]["retained_imports"]),
                    ANALYZER.RUNTIME_IMPORTS)

    def test_relocation_initialization_is_complete_and_bounded(self) -> None:
        offsets = self.initialization["relocation_offsets"]
        relocated = ANALYZER.relocate_table(
            self.template(), offsets, 0x00600000, 0x1000)
        self.assertEqual(len(relocated), 404)
        for index, offset in enumerate(offsets):
            self.assertEqual(struct.unpack_from("<I", relocated, offset)[0],
                             0x00600000 + 4 * (index + 1))
        self.assertTrue(all(
            struct.unpack_from("<I", relocated, offset)[0] == 0
            for offset in range(0, 404, 4) if offset not in offsets))

    def test_hostile_relocation_templates_fail_closed(self) -> None:
        offsets = self.initialization["relocation_offsets"]
        template = self.template()
        cases = [
            (template[:-4], offsets, 0x00600000, 0x1000),
            (template, offsets[:-1], 0x00600000, 0x1000),
            (template, offsets + [offsets[-1]], 0x00600000, 0x1000),
            (template, [*offsets[:-1], 398], 0x00600000, 0x1000),
            (template, offsets, 0x00600004, 0x1000),
            (template, offsets, 0xFFFFF000, 0x2000),
        ]
        missing_pointer = bytearray(template)
        struct.pack_into("<I", missing_pointer, offsets[0], 0)
        cases.append((bytes(missing_pointer), offsets, 0x00600000, 0x1000))
        unexpected_pointer = bytearray(template)
        zero_offset = next(offset for offset in range(0, 404, 4)
                           if offset not in offsets)
        struct.pack_into("<I", unexpected_pointer, zero_offset, 4)
        cases.append((bytes(unexpected_pointer), offsets, 0x00600000, 0x1000))
        escaped = bytearray(template)
        struct.pack_into("<I", escaped, offsets[0], 0x1000)
        cases.append((bytes(escaped), offsets, 0x00600000, 0x1000))
        for index, args in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(ANALYZER.DataPolicyError):
                    ANALYZER.relocate_table(*args)

    def test_xip_layout_rejects_alignment_overlap_and_protected_ranges(self
            ) -> None:
        rodata_start = 0x00700000
        rodata_size = 60316
        table_start = ANALYZER.align_up(
            rodata_start + rodata_size, ANALYZER.TABLE_ALIGNMENT)
        valid = ANALYZER.validate_xip_layout(
            flash_start=0x00600000, flash_end=0x00800000,
            rodata_start=rodata_start, rodata_size=rodata_size,
            table_start=table_start, table_size=404,
            forbidden=((0x007F0000, 0x007F0100),))
        self.assertEqual(valid["runtime_copy_bytes"], 0)
        self.assertEqual(valid["runtime_writable_bytes"], 0)
        mutations = (
            {"rodata_start": rodata_start + 4},
            {"table_start": table_start + 4},
            {"table_size": 400},
            {"table_start": table_start + 8},
            {"flash_end": table_start + 403},
            {"forbidden": ((table_start, table_start + 4),)},
        )
        base = {
            "flash_start": 0x00600000, "flash_end": 0x00800000,
            "rodata_start": rodata_start, "rodata_size": rodata_size,
            "table_start": table_start, "table_size": 404,
            "forbidden": (),
        }
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                args = {**base, **mutation}
                with self.assertRaises(ANALYZER.DataPolicyError):
                    ANALYZER.validate_xip_layout(**args)

    def test_adapter_composition_requires_exact_nonoverlapping_ram(self) -> None:
        valid = ANALYZER.validate_adapter_state_layout(
            ram_start=0x20000000, ram_end=0x20020000,
            state_start=0x20010000,
            occupied=((0x20000000, 0x20003000),))
        self.assertEqual(valid["runtime_writable_bytes"], 10512)
        self.assertEqual(self.report["composition"], {
            "table_flash_bytes": 404,
            "table_runtime_writable_bytes": 0,
            "adapter_state_count": 4,
            "adapter_state_bytes_each": 2628,
            "adapter_state_runtime_writable_bytes": 10512,
            "combined_runtime_writable_bytes": 10512,
            "additional_runtime_writable_bytes": 0,
            "stock_context_total_bytes": 10512,
            "adapter_state_deficit_over_stock_bytes": 0,
            "writable_placement_assigned": True,
            "writable_placement_scope": "authenticated-stock-context-slots",
        })
        cases = (
            {"state_start": 0x20010004},
            {"state_start": 0x2001E000},
            {"state_count": 3},
            {"occupied": ((0x20010000, 0x20010008),)},
        )
        base = {
            "ram_start": 0x20000000, "ram_end": 0x20020000,
            "state_start": 0x20010000, "state_count": 4,
            "occupied": (),
        }
        for index, mutation in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(ANALYZER.DataPolicyError):
                    ANALYZER.validate_adapter_state_layout(
                        **{**base, **mutation})

    def test_manifest_drift_or_routing_promotion_is_rejected(self) -> None:
        mutations = []
        wrong_hash = copy.deepcopy(self.manifest)
        wrong_hash["expected"]["baseline"]["specialized_data_sha256"] = "0" * 64
        mutations.append(wrong_hash)
        writable = copy.deepcopy(self.manifest)
        writable["expected"]["profiles"]["apple-clang"][
            "post_policy_object"]["allocated_writable_sections"] = [".data"]
        mutations.append(writable)
        routed = copy.deepcopy(self.manifest)
        routed["expected"]["routing"]["service_audio_routed"] = True
        mutations.append(routed)
        with tempfile.TemporaryDirectory(
                prefix="opencfw-lc3-data-policy-hostile-") as directory:
            for index, manifest in enumerate(mutations):
                with self.subTest(case=index):
                    path = Path(directory) / f"policy-{index}.json"
                    path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaises(ANALYZER.DataPolicyError):
                        ANALYZER.validate_admission(path, self.report)


if __name__ == "__main__":
    unittest.main()
