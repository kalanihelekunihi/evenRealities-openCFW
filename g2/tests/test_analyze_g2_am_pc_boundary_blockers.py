import json
import unittest

from tools import analyze_g2_am_pc_boundary_blockers as analyzer


class G2AmPcBoundaryBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_pc_boundary_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["blocker_count"], 1039)
        self.assertEqual(self.report["blocker_bytes"], 349200)
        self.assertEqual(self.report["pc_reference_count"], 2045)
        self.assertEqual(
            self.report["relation_counts"],
            {
                "inside_body": 1,
                "outside_body": 184,
                "pc_address_arithmetic": 49,
                "pc_control_operand": 1549,
                "pc_general_operand": 262,
            },
        )

    def test_every_blocker_has_pc_reference_evidence(self) -> None:
        self.assertTrue(all(
            blocker["pc_reference_count"] > 0
            for blocker in self.report["blockers"]
        ))

    def test_am142_first_function_pc_boundary_is_control_returns(self) -> None:
        blocker = next(
            row for row in self.report["blockers"]
            if row["function"] == "open_cfw_runtime_am142_0x0059aa84"
        )
        self.assertEqual(blocker["byte_length"], 2610)
        self.assertEqual(blocker["pc_reference_count"], 17)
        self.assertEqual(
            blocker["pc_reference_relation_counts"],
            {"pc_control_operand": 17},
        )
        self.assertEqual(blocker["return_terminated_segment_count"], 18)
        self.assertEqual(
            blocker["unresolved_source_field_path_counts"],
            {
                "r0+0x224->+0x4": 1,
                "r0+0x224->+0xc": 1,
            },
        )
        self.assertEqual(
            [
                {
                    key: row[key]
                    for key in ("start_offset", "end_offset", "byte_length")
                }
                for row in blocker["largest_return_terminated_segments"][:4]
            ],
            [
                {"start_offset": 302, "end_offset": 934, "byte_length": 632},
                {"start_offset": 1456, "end_offset": 1986, "byte_length": 530},
                {"start_offset": 0, "end_offset": 302, "byte_length": 302},
                {"start_offset": 2140, "end_offset": 2302, "byte_length": 162},
            ],
        )
        largest_segment = blocker["largest_return_terminated_segments"][0]
        self.assertEqual(
            largest_segment["branch_site_counts"],
            {
                "branch:inside_function": 26,
                "call:indirect_or_no_imm": 2,
                "call:inside_function": 6,
                "call:outside_function": 14,
            },
        )
        self.assertEqual(
            largest_segment["branch_target_owner_counts"],
            {
                (
                    "apollo_main:opaque_after_iar_runtime_before_"
                    "easylogger_control_split_00004fb0_00005280_split_"
                    "000050e8_00005280:official_blob"
                ): 1,
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob"
                ): 7,
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob"
                ): 36,
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite"
                ): 2,
                "unresolved:indirect_or_no_imm": 2,
            },
        )
        self.assertEqual(
            [
                (
                    row["owner"],
                    row["target_address"],
                    row["target_owner"]["offset_in_region"],
                    row["count"],
                )
                for row in largest_segment["branch_target_site_frontier"][:4]
            ],
            [
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob",
                    5162868,
                    29356,
                    6,
                ),
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    5876280,
                    10236,
                    3,
                ),
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    5876868,
                    10824,
                    2,
                ),
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    5877194,
                    11150,
                    2,
                ),
            ],
        )
        self.assertEqual(
            largest_segment["branch_target_site_frontier"][0][
                "call_site_examples"][:2],
            [
                {
                    "offset": 320,
                    "instruction": "bl #0x4ec774",
                    "target_offset": -713488,
                    "target_relation": "outside_function",
                },
                {
                    "offset": 700,
                    "instruction": "bl #0x4ec774",
                    "target_offset": -713488,
                    "target_relation": "outside_function",
                },
            ],
        )
        self.assertEqual(
            largest_segment["unresolved_source_field_path_counts"],
            {
                "r0+0x224->+0x4": 1,
                "r0+0x224->+0xc": 1,
            },
        )
        self.assertEqual(
            [
                {
                    key: row[key]
                    for key in (
                        "offset",
                        "instruction",
                        "target_offset",
                        "target_relation",
                        "unresolved_kind",
                        "source_register",
                        "source_register_last_write",
                        "source_base_register",
                        "source_base_register_last_write",
                        "source_field_path",
                    )
                }
                for row in largest_segment["unresolved_branch_site_examples"]
            ],
            [
                {
                    "offset": 460,
                    "instruction": "blx ip",
                    "target_offset": None,
                    "target_relation": "indirect_or_no_imm",
                    "unresolved_kind": "indirect_or_no_imm",
                    "source_register": "ip",
                    "source_register_last_write": {
                        "offset": 456,
                        "instruction": "ldr.w ip, [fp, #0xc]",
                    },
                    "source_base_register": "fp",
                    "source_base_register_last_write": {
                        "offset": 396,
                        "instruction": "ldr.w fp, [r4, #0x224]",
                    },
                    "source_field_path": "r0+0x224->+0xc",
                },
                {
                    "offset": 480,
                    "instruction": "blx r7",
                    "target_offset": None,
                    "target_relation": "indirect_or_no_imm",
                    "unresolved_kind": "indirect_or_no_imm",
                    "source_register": "r7",
                    "source_register_last_write": {
                        "offset": 476,
                        "instruction": "ldr.w r7, [fp, #4]",
                    },
                    "source_base_register": "fp",
                    "source_base_register_last_write": {
                        "offset": 396,
                        "instruction": "ldr.w fp, [r4, #0x224]",
                    },
                    "source_field_path": "r0+0x224->+0x4",
                },
            ],
        )
        self.assertEqual(
            [
                row["source_pointer_chain"]
                for row in largest_segment["unresolved_branch_site_examples"]
            ],
            [
                [
                    {
                        "register": "ip",
                        "source_kind": "memory_load",
                        "base_register": "fp",
                        "field_offset": 12,
                        "load_offset": 456,
                        "instruction": "ldr.w ip, [fp, #0xc]",
                    },
                    {
                        "register": "fp",
                        "source_kind": "memory_load",
                        "base_register": "r4",
                        "field_offset": 548,
                        "load_offset": 396,
                        "instruction": "ldr.w fp, [r4, #0x224]",
                    },
                    {
                        "register": "r4",
                        "source_register": "r0",
                        "source_kind": "register_move",
                        "write": {
                            "offset": 336,
                            "instruction": "movs r4, r0",
                        },
                    },
                ],
                [
                    {
                        "register": "r7",
                        "source_kind": "memory_load",
                        "base_register": "fp",
                        "field_offset": 4,
                        "load_offset": 476,
                        "instruction": "ldr.w r7, [fp, #4]",
                    },
                    {
                        "register": "fp",
                        "source_kind": "memory_load",
                        "base_register": "r4",
                        "field_offset": 548,
                        "load_offset": 396,
                        "instruction": "ldr.w fp, [r4, #0x224]",
                    },
                    {
                        "register": "r4",
                        "source_register": "r0",
                        "source_kind": "register_move",
                        "write": {
                            "offset": 336,
                            "instruction": "movs r4, r0",
                        },
                    },
                ],
            ],
        )
        self.assertEqual(
            largest_segment["branch_site_examples"][:3],
            [
                {
                    "offset": 308,
                    "instruction": "bl #0x4ec626",
                    "target_offset": -713822,
                    "target_relation": "outside_function",
                    "target_owner": {
                        "component": "apollo_main",
                        "region": (
                            "opaque_after_pb_even_ai_before_"
                            "ring_battery_service"
                        ),
                        "address_status": "official_blob",
                        "region_start": 0x004E54C8,
                        "offset_in_region": 29022,
                    },
                },
                {
                    "offset": 320,
                    "instruction": "bl #0x4ec774",
                    "target_offset": -713488,
                    "target_relation": "outside_function",
                    "target_owner": {
                        "component": "apollo_main",
                        "region": (
                            "opaque_after_pb_even_ai_before_"
                            "ring_battery_service"
                        ),
                        "address_status": "official_blob",
                        "region_start": 0x004E54C8,
                        "offset_in_region": 29356,
                    },
                },
                {
                    "offset": 328,
                    "instruction": "b #0x59ab96",
                    "target_offset": 274,
                    "target_relation": "inside_function",
                    "target_owner": {
                        "component": "apollo_main",
                        "region": (
                            "opaque_between_ring_buffer_and_"
                            "pb_translate_split_0016025c_00165264"
                        ),
                        "address_status": "official_blob",
                        "region_start": 0x0059823C,
                        "offset_in_region": 10586,
                    },
                },
            ],
        )
        self.assertEqual(
            blocker["pc_references"][0],
            {
                "offset": 300,
                "instruction": "pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}",
                "target_offset": None,
                "target_relation": "pc_control_operand",
            },
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
