import json
import unittest

from tools import analyze_g2_apollo_retained_hot_targets as analyzer


class G2ApolloRetainedHotTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = analyzer.analyze()

    def test_hot_targets_are_ranked_from_focused_frontier(self) -> None:
        self.assertEqual(self.report["firmware_base"], 0x00437FE0)
        self.assertEqual(self.report["window_bytes"], 96)
        self.assertEqual(self.report["hot_target_count"], 10)
        self.assertEqual(
            self.report["target_shape_counts"],
            {
                "branch_trampoline_or_midblock_label": 1,
                "direct_subroutine_entry": 7,
                "nondecoding_branch_target": 2,
            },
        )
        self.assertEqual(
            [
                (
                    row["count"],
                    row["target_address"],
                    row["region"],
                    row["offset_in_region"],
                )
                for row in self.report["hot_targets"][:5]
            ],
            [
                (
                    19,
                    0x004EC718,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29264,
                ),
                (
                    16,
                    0x004EC774,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29356,
                ),
                (
                    12,
                    0x0059C766,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    17706,
                ),
                (
                    8,
                    0x0059D15E,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    20258,
                ),
                (
                    7,
                    0x0059BC26,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    14826,
                ),
            ],
        )

    def test_ring_battery_adjacent_hot_targets_decode_as_direct_subroutines(self) -> None:
        first, second = self.report["hot_targets"][:2]
        self.assertEqual(
            (
                first["target_shape"],
                first["instruction_count"],
                first["window_sha256"],
                first["control_flow_counts"],
                first["control_flow_owner_counts"],
                first["call_relation_counts"],
                second["target_shape"],
                second["instruction_count"],
                second["window_sha256"],
                second["control_flow_counts"],
                second["control_flow_owner_counts"],
                second["call_relation_counts"],
            ),
            (
                "direct_subroutine_entry",
                32,
                "9aa53f99d944ea1c0a955bc9a112875e3da595ff1459aecc25a194716ce7f41e",
                {"call": 6, "jump": 8},
                {
                    (
                        "apollo_main:opaque_after_easylogger_hexdump_before_"
                        "freertos_queue_reset_split_00006f90_00009536:"
                        "official_blob"
                    ): 2,
                    (
                        "apollo_main:opaque_after_pb_even_ai_before_"
                        "ring_battery_service:official_blob"
                    ): 4,
                    (
                        "apollo_main:opaque_between_kvdb_module_configure_and_"
                        "kvdb_universal_setting:official_blob"
                    ): 2,
                },
                {"outside_function": 8},
                "direct_subroutine_entry",
                34,
                "70ecb6d4db544f1695f03d44324ea075eb37cbc71fe6455928338eda3c162d21",
                {"call": 7, "jump": 11},
                {
                    (
                        "apollo_main:opaque_after_easylogger_hexdump_before_"
                        "freertos_queue_reset_split_00005ca8_0000621a:"
                        "official_blob"
                    ): 2,
                    (
                        "apollo_main:opaque_after_easylogger_hexdump_before_"
                        "freertos_queue_reset_split_00006f90_00009536:"
                        "official_blob"
                    ): 1,
                    (
                        "apollo_main:opaque_after_pb_even_ai_before_"
                        "ring_battery_service:official_blob"
                    ): 4,
                    (
                        "apollo_main:opaque_between_kvdb_module_configure_and_"
                        "kvdb_universal_setting:official_blob"
                    ): 4,
                },
                {"outside_function": 8},
            ),
        )
        self.assertEqual(
            first["call_site_examples"][:3],
            [
                {
                    "instruction": "bl #0x4ec718",
                    "offset": 16,
                    "target_offset": -713580,
                    "target_relation": "outside_function",
                },
                {
                    "instruction": "bl #0x4ec718",
                    "offset": 56,
                    "target_offset": -713580,
                    "target_relation": "outside_function",
                },
                {
                    "instruction": "bl #0x4ec718",
                    "offset": 78,
                    "target_offset": -717772,
                    "target_relation": "outside_function",
                },
            ],
        )
        self.assertEqual(
            [row["instruction"] for row in first["instructions"][:6]],
            [
                "mov r0, sl",
                "bl #0x44104c",
                "movs r2, #0",
                "movs r1, r0",
                "ldr.w r0, [r8]",
                "bl #0x44140e",
            ],
        )
        self.assertEqual(
            [row["instruction"] for row in second["instructions"][:6]],
            [
                "mov sb, r0",
                "movs r2, #3",
                "movs r1, #0",
                "mov r0, sb",
                "bl #0x43f09a",
                "movs.w r1, #0x10000",
            ],
        )

    def test_ring_buffer_targets_record_non_decoding_boundaries(self) -> None:
        target = self.report["hot_targets"][2]
        self.assertEqual(target["target_address"], 0x0059C766)
        self.assertEqual(target["target_shape"], "nondecoding_branch_target")
        self.assertEqual(target["instruction_count"], 0)
        self.assertEqual(target["call_relation_counts"], {"inside_function": 8})
        self.assertEqual(target["instructions"], [])
        self.assertEqual(
            target["call_site_examples"][:3],
            [
                {
                    "instruction": "beq.w #0x59c766",
                    "offset": 988,
                    "target_offset": 1378,
                    "target_relation": "inside_function",
                },
                {
                    "instruction": "b #0x59c766",
                    "offset": 1034,
                    "target_offset": 1378,
                    "target_relation": "inside_function",
                },
                {
                    "instruction": "b #0x59c766",
                    "offset": 1062,
                    "target_offset": 1378,
                    "target_relation": "inside_function",
                },
            ],
        )

    def test_direct_subroutine_frontier_is_ranked(self) -> None:
        self.assertEqual(
            [
                (
                    row["count"],
                    row["target_address"],
                    row["region"],
                    row["offset_in_region"],
                    row["instruction_count"],
                    row["window_sha256"],
                    row["dependency_class"],
                    row["external_dependency_count"],
                    row["first_instruction"],
                )
                for row in self.report["direct_subroutine_frontier"][:5]
            ],
            [
                (
                    19,
                    0x004EC718,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29264,
                    32,
                    "9aa53f99d944ea1c0a955bc9a112875e3da595ff1459aecc25a194716ce7f41e",
                    "cross_retained_dependency",
                    4,
                    "mov r0, sl",
                ),
                (
                    16,
                    0x004EC774,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29356,
                    34,
                    "70ecb6d4db544f1695f03d44324ea075eb37cbc71fe6455928338eda3c162d21",
                    "cross_retained_dependency",
                    7,
                    "mov sb, r0",
                ),
                (
                    7,
                    0x0059C060,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    15908,
                    35,
                    "e5cba481e8874eca132e21d241fcc065ab1a90bf01080eba563a1f8ee53bc392",
                    "same_retained_interval_only",
                    0,
                    "sub.w lr, sl, ip",
                ),
                (
                    5,
                    0x0059BA4A,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    14350,
                    35,
                    "193506cbbba1e3b8780e00263932dd4346d628915efadd0002286ec7526adf66",
                    "same_retained_interval_only",
                    0,
                    "add.w r0, r1, #0x400",
                ),
                (
                    4,
                    0x0059A312,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    8406,
                    29,
                    "3722bbac32feadde6813205022c9ac71020f38eb3ded4289e33f99c7fb347887",
                    "isolated_window",
                    0,
                    "subs r4, r1, r0",
                ),
            ],
        )

    def test_source_pull_through_queue_prioritizes_low_dependency_candidates(self) -> None:
        self.assertEqual(
            [
                (
                    row["priority"],
                    row["target_address"],
                    row["dependency_class"],
                    row["external_dependency_count"],
                    row["count"],
                    row["bounded_span_byte_length"],
                    row["bounded_span_sha256"],
                    row["bounded_span_status"],
                    row["ingress_call_site_count"],
                    tuple(
                        (caller["function"], caller["count"])
                        for caller in row["ingress_caller_functions"]
                    ),
                    row["first_instruction"],
                )
                for row in self.report["source_pull_through_queue"]
            ],
            [
                (
                    1,
                    0x0059A312,
                    "isolated_window",
                    0,
                    4,
                    148,
                    "96ee3a14b8c5ec1e2d5db900774b5ed82c2326b5b6002b0974bad0f5c782b39d",
                    "terminated_at_control_flow",
                    4,
                    (
                        ("open_cfw_runtime_am142_0x0059cf1a", 3),
                        ("open_cfw_runtime_am142_0x0059bae4", 1),
                    ),
                    "subs r4, r1, r0",
                ),
                (
                    2,
                    0x0059A32E,
                    "isolated_window",
                    0,
                    4,
                    120,
                    "3a7cb09e0b634d07376680220ee90bcf54749251cc753bce9407db39a62453f9",
                    "terminated_at_control_flow",
                    4,
                    (
                        ("open_cfw_runtime_am142_0x0059cf1a", 3),
                        ("open_cfw_runtime_am142_0x0059bae4", 1),
                    ),
                    "cmp r2, #0xc2",
                ),
                (
                    3,
                    0x0059C060,
                    "same_retained_interval_only",
                    0,
                    7,
                    28,
                    "5b9577a8b15ccbfa3ea36193555314de934217541a7c37767928e94db1ca92f5",
                    "terminated_at_control_flow",
                    7,
                    (
                        ("open_cfw_runtime_am142_0x0059c204", 7),
                    ),
                    "sub.w lr, sl, ip",
                ),
                (
                    4,
                    0x0059BA4A,
                    "same_retained_interval_only",
                    0,
                    5,
                    10,
                    "60a31fe274a20db0a48e19f70e6546471dba3728cd62679912af4c2c5375dbfc",
                    "terminated_at_control_flow",
                    5,
                    (
                        ("open_cfw_runtime_am142_0x0059bae4", 5),
                    ),
                    "add.w r0, r1, #0x400",
                ),
                (
                    5,
                    0x0059A3D2,
                    "same_retained_interval_only",
                    0,
                    4,
                    68,
                    "b4abb9c17fbe4f41122edf23c0e0ca34f1a6a6e3e02020c8ad090f348d2b0eb8",
                    "terminated_at_control_flow",
                    4,
                    (
                        ("open_cfw_runtime_am142_0x0059bae4", 3),
                        ("open_cfw_runtime_am142_0x0059b852", 1),
                    ),
                    "movs r2, #1",
                ),
                (
                    6,
                    0x004EC718,
                    "cross_retained_dependency",
                    4,
                    19,
                    6,
                    "00aac9d2c1d7199df4e0b4e4e49be24319cfa7cdaf40db1f5aa4cbdc02891dc5",
                    "terminated_at_control_flow",
                    62,
                    (
                        ("open_cfw_runtime_am142_0x0059bae4", 9),
                        ("open_cfw_runtime_am142_0x0059c204", 8),
                        ("open_cfw_runtime_am144_0x005a05e0", 5),
                    ),
                    "mov r0, sl",
                ),
                (
                    7,
                    0x004EC774,
                    "cross_retained_dependency",
                    7,
                    16,
                    12,
                    "0394d1e0c12344b77c620869e4afdb0e15f73890d8709ab7db1484342114af46",
                    "terminated_at_control_flow",
                    29,
                    (
                        ("open_cfw_runtime_am142_0x0059aa84", 14),
                        ("open_cfw_runtime_am141_0x00599714", 3),
                        ("open_cfw_runtime_am150_0x005b8bc8", 3),
                    ),
                    "mov sb, r0",
                ),
            ],
        )

    def test_source_pull_through_clusters_merge_overlapping_spans(self) -> None:
        first_cluster = self.report["source_pull_through_clusters"][0]
        rollup = self.report["source_pull_through_recovery_rollup"]
        self.assertEqual(
            {key: rollup[key] for key in (
                "all_require_c_pull_through",
                "byte_length",
                "cluster_count",
                "dependency_class_counts",
                "implementation_readiness_counts",
                "instruction_count",
                "semantic_model_contract_complete",
                "semantic_model_contract_count",
                "semantic_model_firmware_routing_status_counts",
                "semantic_model_kind_counts",
                "status_counts",
            )},
            {
                "all_require_c_pull_through": True,
                "byte_length": 272,
                "cluster_count": 6,
                "dependency_class_counts": {
                    "cross_retained_dependency": 2,
                    "isolated_window": 1,
                    "same_retained_interval_only": 3,
                },
                "implementation_readiness_counts": {
                    "needs_cross_retained_dependency_resolution": 2,
                    "needs_same_interval_context": 3,
                    "ready_for_direct_c_translation": 1,
                },
                "instruction_count": 80,
                "semantic_model_contract_complete": True,
                "semantic_model_contract_count": 6,
                "semantic_model_firmware_routing_status_counts": {
                    "not_yet_routed_into_overlay": 6,
                },
                "semantic_model_kind_counts": {
                    "call_shim_to_retained_helper": 2,
                    "integer_affine_index_update": 1,
                    "squared_delta_accumulator": 1,
                    "stack_parabolic_compare_branch": 1,
                    "threshold_offset_branch": 1,
                },
                "status_counts": {
                    "requires_c_pull_through": 6,
                },
            },
        )
        self.assertEqual(
            rollup["am142_target_compile_receipt"],
            {
                "available": True,
                "manifest": (
                    "tools/manifests/"
                    "g2-apollo-am142-pullthrough-candidate.json"
                ),
                "source": (
                    "components/apollo_main/core_overlay/"
                    "runtime_liblc3_am142_semantic_model.c"
                ),
                "source_sha256": (
                    "fe06bf45dd19a0c595fdb0c4277f12f37cd801d79e130f6271a0889aeceb64e9"
                ),
                "toolchain_profile": "apple-clang",
                "target": "thumbv7em-none-eabi",
                "object_size": 4976,
                "object_sha256": (
                    "273ca76794e7ba222098acaaa9913a6d5e5effb741f95c23bc755c3eecfcf43c"
                ),
                "symbol_count": 28,
                "undefined_symbol_count": 0,
                "relocation_count": 28,
                "relocation_summary": [
                    {
                        "count": 28,
                        "section": ".ARM.exidx",
                        "type": "R_ARM_PREL31",
                        "value": ".text",
                    },
                ],
                "target_compile_verified": True,
                "firmware_routing_status": "not_yet_routed_into_overlay",
            },
        )
        self.assertEqual(
            [
                (
                    row["priority"],
                    row["start_address"],
                    row["byte_length"],
                    row["instruction_count"],
                    row["dependency_class"],
                    row["implementation_readiness"],
                    row["dependency_barrier"],
                    row["memory_instruction_count"],
                    row["vfp_instruction_count"],
                    row["entrypoint_count"],
                    row["terminal_instruction"],
                    row["arithmetic_motif_kind"],
                )
                for row in rollup["work_items"]
            ],
            [
                (
                    1,
                    0x0059A312,
                    148,
                    44,
                    "isolated_window",
                    "ready_for_direct_c_translation",
                    None,
                    9,
                    26,
                    2,
                    "bge #0x59a45c",
                    "squared_delta_accumulator",
                ),
                (
                    2,
                    0x0059C060,
                    28,
                    8,
                    "same_retained_interval_only",
                    "needs_same_interval_context",
                    "terminal target stays inside the same retained interval",
                    0,
                    0,
                    1,
                    "b #0x59c086",
                    "integer_affine_index_update",
                ),
                (
                    3,
                    0x0059BA4A,
                    10,
                    3,
                    "same_retained_interval_only",
                    "needs_same_interval_context",
                    "terminal target stays inside the same retained interval",
                    0,
                    0,
                    1,
                    "ble.w #0x59b8b2",
                    "threshold_offset_branch",
                ),
                (
                    4,
                    0x0059A3D2,
                    68,
                    18,
                    "same_retained_interval_only",
                    "needs_same_interval_context",
                    "terminal target stays inside the same retained interval",
                    2,
                    12,
                    1,
                    "bpl #0x59a420",
                    "stack_parabolic_compare_branch",
                ),
                (
                    5,
                    0x004EC718,
                    6,
                    2,
                    "cross_retained_dependency",
                    "needs_cross_retained_dependency_resolution",
                    "terminal target depends on a different retained owner",
                    0,
                    0,
                    1,
                    "bl #0x44104c",
                    "call_shim_to_retained_helper",
                ),
                (
                    6,
                    0x004EC774,
                    12,
                    5,
                    "cross_retained_dependency",
                    "needs_cross_retained_dependency_resolution",
                    "terminal target depends on a different retained owner",
                    0,
                    0,
                    1,
                    "bl #0x43f09a",
                    "call_shim_to_retained_helper",
                ),
            ],
        )
        self.assertEqual(
            [
                (
                    row["priority"],
                    row["start_address"],
                    row["end_address"],
                    row["byte_length"],
                    row["dependency_class"],
                    row["total_call_site_count"],
                    row["sha256"],
                    [
                        (target["target_address"], target[
                            "bounded_span_byte_length"])
                        for target in row["targets"]
                    ],
                    [
                        (caller["function"], caller["count"])
                        for caller in row["caller_functions"][:2]
                    ],
                )
                for row in self.report["source_pull_through_clusters"][:4]
            ],
            [
                (
                    1,
                    0x0059A312,
                    0x0059A3A6,
                    148,
                    "isolated_window",
                    8,
                    "96ee3a14b8c5ec1e2d5db900774b5ed82c2326b5b6002b0974bad0f5c782b39d",
                    [(0x0059A312, 148), (0x0059A32E, 120)],
                    [
                        ("open_cfw_runtime_am142_0x0059cf1a", 6),
                        ("open_cfw_runtime_am142_0x0059bae4", 2),
                    ],
                ),
                (
                    2,
                    0x0059C060,
                    0x0059C07C,
                    28,
                    "same_retained_interval_only",
                    7,
                    "5b9577a8b15ccbfa3ea36193555314de934217541a7c37767928e94db1ca92f5",
                    [(0x0059C060, 28)],
                    [("open_cfw_runtime_am142_0x0059c204", 7)],
                ),
                (
                    3,
                    0x0059BA4A,
                    0x0059BA54,
                    10,
                    "same_retained_interval_only",
                    5,
                    "60a31fe274a20db0a48e19f70e6546471dba3728cd62679912af4c2c5375dbfc",
                    [(0x0059BA4A, 10)],
                    [("open_cfw_runtime_am142_0x0059bae4", 5)],
                ),
                (
                    4,
                    0x0059A3D2,
                    0x0059A416,
                    68,
                    "same_retained_interval_only",
                    4,
                    "b4abb9c17fbe4f41122edf23c0e0ca34f1a6a6e3e02020c8ad090f348d2b0eb8",
                    [(0x0059A3D2, 68)],
                    [
                        ("open_cfw_runtime_am142_0x0059bae4", 3),
                        ("open_cfw_runtime_am142_0x0059b852", 1),
                    ],
                ),
            ],
        )
        self.assertEqual(
            (
                first_cluster["instruction_count"],
                first_cluster["instructions"][0]["instruction"],
                first_cluster["instructions"][-2]["instruction"],
                first_cluster["instructions"][-1]["instruction"],
                first_cluster["instructions"][-1]["target_address"],
            ),
            (
                44,
                "subs r4, r1, r0",
                "cmp r2, #0xa",
                "bge #0x59a45c",
                0x0059A45C,
            ),
        )
        self.assertEqual(
            (
                first_cluster["source_recovery_status"]["status"],
                first_cluster["source_recovery_status"][
                    "current_representation"],
                first_cluster["source_recovery_status"]["decoded"],
                first_cluster["source_recovery_status"]["byte_length"],
                [
                    (
                        row["target_address"],
                        row["bounded_span_byte_length"],
                        row["call_site_count"],
                    )
                    for row in first_cluster["source_recovery_status"][
                        "entrypoints"]
                ],
                first_cluster["source_recovery_status"][
                    "terminal_branch"]["instruction"],
                first_cluster["source_recovery_status"][
                    "terminal_branch"]["target_address"],
            ),
            (
                "requires_c_pull_through",
                "retained_exact_helper_bytes",
                True,
                148,
                [(0x0059A312, 148, 4), (0x0059A32E, 120, 4)],
                "bge #0x59a45c",
                0x0059A45C,
            ),
        )
        self.assertEqual(
            (
                first_cluster["source_recovery_status"][
                    "translation_summary"]["shape"],
                first_cluster["source_recovery_status"][
                    "translation_summary"]["instruction_count"],
                first_cluster["source_recovery_status"][
                    "translation_summary"]["memory_instruction_count"],
                first_cluster["source_recovery_status"][
                    "translation_summary"]["vfp_instruction_count"],
                first_cluster["source_recovery_status"][
                    "translation_summary"]["mnemonic_counts"]["vmls.f32"],
                first_cluster["source_recovery_status"][
                    "translation_summary"]["mnemonic_counts"]["vsub.f32"],
                len(first_cluster["source_recovery_status"][
                    "source_obligations"]),
            ),
            (
                "straight_line_to_terminal_branch",
                44,
                9,
                26,
                4,
                4,
                4,
            ),
        )
        self.assertEqual(
            {
                key: first_cluster["feature_summary"][key]
                for key in (
                    "memory_reads",
                    "memory_writes",
                    "vfp_reads",
                    "vfp_writes",
                )
            },
            {
                "memory_reads": {
                    "r5+0xb4": 1,
                    "r5+0xb8": 1,
                    "r5+0xbc": 1,
                    "r6+0x34": 1,
                    "r6+0x38": 1,
                    "r6+0x3c": 1,
                },
                "memory_writes": {
                    "sp+0x13c": 1,
                    "sp+0x140": 1,
                    "sp+0x144": 1,
                },
                "vfp_reads": {
                    "s2": 1,
                    "s3": 2,
                    "s4": 3,
                    "s5": 3,
                    "s6": 1,
                    "s7": 2,
                },
                "vfp_writes": {
                    "s16": 4,
                    "s3": 1,
                    "s4": 5,
                    "s5": 6,
                    "s6": 6,
                    "s7": 4,
                },
            },
        )
        self.assertEqual(
            first_cluster["arithmetic_motif"],
            {
                "kind": "squared_delta_accumulator",
                "initial_integer_delta": "r1-r0",
                "accumulator_register": "s16",
                "input_value_count": 3,
                "coefficient_count": 3,
                "stack_zero_count": 3,
                "lanes": [
                    {
                        "lane": 1,
                        "value_base": "r5",
                        "value_offset": 180,
                        "coefficient_base": "r6",
                        "coefficient_offset": 52,
                        "stack_zero_offset": 316,
                    },
                    {
                        "lane": 2,
                        "value_base": "r5",
                        "value_offset": 184,
                        "coefficient_base": "r6",
                        "coefficient_offset": 56,
                        "stack_zero_offset": 320,
                    },
                    {
                        "lane": 3,
                        "value_base": "r5",
                        "value_offset": 188,
                        "coefficient_base": "r6",
                        "coefficient_offset": 60,
                        "stack_zero_offset": 324,
                    },
                ],
                "terminal_compare": {
                    "instruction": "cmp r2, #0xa",
                    "branch_instruction": "bge #0x59a45c",
                    "branch_target": 0x0059A45C,
                },
                "source_model": {
                    "summary": (
                        "accumulate four weighted squared/delta terms, derive a "
                        "terminal residual integer delta, and branch when that "
                        "residual is at least ten"
                    ),
                    "state_inputs": [
                        "r0",
                        "r1",
                        "s2",
                        "s3",
                        "s16",
                        "uint32_t *(r5+0xb4..0xbc)",
                        "float *(r6+0x34..0x3c)",
                    ],
                    "operations": [
                        "r4 = r1 - r0",
                        "s16 -= float(s4) * s2",
                        "stack[0x13c] = 0",
                        "d1 = load32(r5 + 0xb4); r0 -= d1; s16 -= float(d1) * coeff[0]",
                        "stack[0x140] = 0",
                        "d2 = load32(r5 + 0xb8); r0 -= d2; s16 -= float(d2) * coeff[1]",
                        "stack[0x144] = 0",
                        "d3 = load32(r5 + 0xbc); residual = r0 - d3; s16 -= float(d3) * coeff[2]",
                        "branch to 0x59a45c when residual >= 10",
                    ],
                    "abi_contract": {
                        "integer_inputs": ["r0", "r1", "r5", "r6"],
                        "integer_outputs": ["r0", "r2", "r4"],
                        "integer_temporaries": ["r1"],
                        "vfp_inputs": ["s2", "s3", "s4", "s16"],
                        "vfp_outputs": ["s4", "s5", "s6", "s7", "s16"],
                        "stack_zero_writes": [
                            {"offset": 0x13C, "value": 0},
                            {"offset": 0x140, "value": 0},
                            {"offset": 0x144, "value": 0},
                        ],
                        "memory_inputs": [
                            {"base": "r5", "offset": 0xB4, "role": "delta_1"},
                            {"base": "r5", "offset": 0xB8, "role": "delta_2"},
                            {"base": "r5", "offset": 0xBC, "role": "delta_3"},
                            {"base": "r6", "offset": 0x34, "role": "coefficient_1"},
                            {"base": "r6", "offset": 0x38, "role": "coefficient_2"},
                            {"base": "r6", "offset": 0x3C, "role": "coefficient_3"},
                        ],
                        "branch_condition": {
                            "residual_register": "r2",
                            "comparison": "r2 >= 10",
                            "target_address": 0x0059A45C,
                        },
                    },
                    "abi_validation": {
                        "matches_decoded_features": True,
                        "observed_r5_offsets": [0xB4, 0xB8, 0xBC],
                        "observed_r6_offsets": [0x34, 0x38, 0x3C],
                        "observed_stack_zero_offsets": [0x13C, 0x140, 0x144],
                        "observed_branch_target": 0x0059A45C,
                        "observed_s16_write_count": 4,
                    },
                    "c_translation_status": (
                        "semantic_model_ready_requires_register_abi_mapping"),
                    "reference_source": (
                        "components/apollo_main/core_overlay/"
                        "runtime_liblc3_am142_semantic_model.c"
                    ),
                    "reference_tests": [
                        "tests/test_runtime_liblc3_am142_semantic_model.py",
                    ],
                    "reference_evidence": {
                        "source_sha256": (
                            "fe06bf45dd19a0c595fdb0c4277f12f"
                            "37cd801d79e130f6271a0889aeceb64e9"
                        ),
                        "test_sha256": (
                            "1a9e2bc27d3d9a82452f3a083f50cd987"
                            "b285b2deb7339c6aad90be4e8d90783"
                        ),
                        "overlay_source_listed": False,
                        "host_test_command": (
                            "python3 -m unittest "
                            "tests.test_runtime_liblc3_am142_semantic_model"
                        ),
                        "host_test_platform": (
                            "macOS clang shared-library build"),
                        "firmware_routing_status": (
                            "not_yet_routed_into_overlay"),
                    },
                },
            },
        )
        second_cluster = self.report["source_pull_through_clusters"][1]
        self.assertEqual(
            (
                second_cluster["arithmetic_motif"]["kind"],
                second_cluster["arithmetic_motif"]["source_model"][
                    "c_translation_status"],
                second_cluster["arithmetic_motif"]["source_model"][
                    "abi_contract"]["wraparound_semantics"],
                second_cluster["arithmetic_motif"]["source_model"][
                    "abi_contract"]["branch_condition"],
                second_cluster["arithmetic_motif"]["source_model"][
                    "abi_validation"]["matches_decoded_features"],
                second_cluster["arithmetic_motif"]["source_model"][
                    "operations"][-1],
            ),
            (
                "integer_affine_index_update",
                "semantic_model_ready_requires_same_interval_routing",
                "uint32_t low-word ARM arithmetic",
                {
                    "comparison": "unconditional",
                    "target_address": 0x0059C086,
                },
                True,
                "branch to 0x59c086",
            ),
        )
        third_cluster = self.report["source_pull_through_clusters"][2]
        self.assertEqual(
            (
                third_cluster["arithmetic_motif"]["kind"],
                third_cluster["arithmetic_motif"]["source_model"][
                    "c_translation_status"],
                third_cluster["arithmetic_motif"]["source_model"][
                    "abi_contract"]["wraparound_semantics"],
                third_cluster["arithmetic_motif"]["source_model"][
                    "abi_contract"]["branch_condition"],
                third_cluster["arithmetic_motif"]["source_model"][
                    "abi_validation"]["matches_decoded_features"],
                third_cluster["arithmetic_motif"]["source_model"][
                    "operations"][-1],
            ),
            (
                "threshold_offset_branch",
                "semantic_model_ready_requires_same_interval_routing",
                "uint32_t low-word add for r0",
                {
                    "comparison": "signed r4 <= 1",
                    "target_address": 0x0059B8B2,
                },
                True,
                "branch to 0x59b8b2 when signed r4 <= 1",
            ),
        )
        fourth_cluster = self.report["source_pull_through_clusters"][3]
        self.assertEqual(
            (
                fourth_cluster["arithmetic_motif"]["kind"],
                fourth_cluster["arithmetic_motif"]["source_model"][
                    "c_translation_status"],
                fourth_cluster["arithmetic_motif"]["source_model"][
                    "abi_contract"]["branch_condition"],
                fourth_cluster["arithmetic_motif"]["source_model"][
                    "abi_validation"]["matches_decoded_features"],
                fourth_cluster["arithmetic_motif"]["source_model"][
                    "operations"][-1],
            ),
            (
                "stack_parabolic_compare_branch",
                "semantic_model_ready_requires_same_interval_routing",
                {
                    "comparison": (
                        "(float((int32_t)(stack_word << 1)) + s6 + "
                        "1.0f) * s7 >= (s16 + stack_float)^2 * s8"
                    ),
                    "target_address": 0x0059A420,
                },
                True,
                "branch to 0x59a420 when s12 >= s11",
            ),
        )
        shim_clusters = self.report["source_pull_through_clusters"][4:6]
        self.assertEqual(
            [
                (
                    cluster["arithmetic_motif"]["kind"],
                    cluster["arithmetic_motif"]["source_model"][
                        "c_translation_status"],
                    cluster["arithmetic_motif"]["source_model"][
                        "abi_contract"]["terminal_call_target"],
                    cluster["arithmetic_motif"]["source_model"][
                        "abi_validation"]["matches_decoded_features"],
                    cluster["arithmetic_motif"]["source_model"][
                        "operations"][-1],
                )
                for cluster in shim_clusters
            ],
            [
                (
                    "call_shim_to_retained_helper",
                    "semantic_model_ready_requires_cross_retained_callee_resolution",
                    0x0044104C,
                    True,
                    "call 0x0044104c",
                ),
                (
                    "call_shim_to_retained_helper",
                    "semantic_model_ready_requires_cross_retained_callee_resolution",
                    0x0043F09A,
                    True,
                    "call 0x0043f09a",
                ),
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
