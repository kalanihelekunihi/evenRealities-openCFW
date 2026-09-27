import json
import unittest

from tools import analyze_g2_source_closure_blocker_index as analyzer


class G2SourceClosureBlockerIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = analyzer.analyze()

    def test_rollup_matches_source_only_blockers(self) -> None:
        self.assertFalse(self.report["source_only_ready"])
        self.assertEqual(self.report["global_blockers"], ["source_ownership_quality"])
        self.assertEqual(self.report["release_blocking_bytes"], 3739673)
        self.assertEqual(
            {
                name: row["release_blocking_bytes"]
                for name, row in self.report["component_blockers"].items()
            },
            {
                "apollo_bootloader": 81187,
                "apollo_main": 3032198,
                "ble_em9305": 210584,
                "case": 55752,
                "codec": 326000,
                "touch": 33952,
            },
        )

    def test_rollup_matches_source_ownership_quality(self) -> None:
        quality = self.report["source_ownership_quality"]
        self.assertFalse(quality["source_ownership_suitable"])
        self.assertEqual(quality["public_unrouted_raw_instruction_source_count"], 102)
        self.assertEqual(quality["public_unrouted_raw_instruction_source_bytes"], 584954)
        self.assertEqual(quality["untracked_overlay_source_input_count"], 0)
        self.assertEqual(
            quality["gate_blocking_metrics"]["public_raw_executable_transcript_files"],
            131,
        )
        self.assertEqual(
            quality["gate_blocking_metrics"][
                "untracked_raw_bearing_overlay_source_inputs"],
            0,
        )
        self.assertEqual(
            quality["context_metrics"]["untracked_overlay_source_inputs"],
            0,
        )
        self.assertEqual(
            (
                quality["context_metrics"][
                    "untracked_raw_bearing_overlay_source_inputs"],
                quality["context_metrics"][
                    "untracked_non_raw_overlay_source_inputs"],
            ),
            (0, 0),
        )
        self.assertEqual(
            quality["raw_transcript_frontier"]["raw_bearing_input_count"],
            0,
        )
        self.assertEqual(
            quality["raw_transcript_frontier"]["raw_bearing_am_helper_ranges"],
            [],
        )
        self.assertEqual(
            quality["raw_transcript_frontier"]["mixed_boundary_reason_counts"][
                "pc_relative_or_pc_operand_needs_boundary_model"],
            98,
        )
        recovery = quality["retained_hot_target_recovery_frontier"]
        self.assertTrue(recovery["available"])
        self.assertEqual(
            (
                recovery["rollup"]["semantic_model_contract_complete"],
                recovery["rollup"]["semantic_model_contract_count"],
                recovery["rollup"][
                    "semantic_model_firmware_routing_status_counts"],
                recovery["rollup"]["semantic_model_kind_counts"],
            ),
            (
                True,
                6,
                {"not_yet_routed_into_overlay": 6},
                {
                    "call_shim_to_retained_helper": 2,
                    "integer_affine_index_update": 1,
                    "squared_delta_accumulator": 1,
                    "stack_parabolic_compare_branch": 1,
                    "threshold_offset_branch": 1,
                },
            ),
        )
        self.assertEqual(
            recovery["rollup"]["work_items"][0],
            {
                "arithmetic_motif_kind": "squared_delta_accumulator",
                "byte_length": 148,
                "dependency_class": "isolated_window",
                "end_address": 0x0059A3A6,
                "entrypoint_count": 2,
                "implementation_readiness": "ready_for_direct_c_translation",
                "dependency_barrier": None,
                "instruction_count": 44,
                "memory_instruction_count": 9,
                "priority": 1,
                "start_address": 0x0059A312,
                "status": "requires_c_pull_through",
                "terminal_instruction": "bge #0x59a45c",
                "translation_shape": "straight_line_to_terminal_branch",
                "vfp_instruction_count": 26,
            },
        )
        focused = quality["raw_transcript_frontier"]["focused_raw_helper_subrange"]
        self.assertEqual(
            (
                focused["top_source_function_frontier"]["number"],
                focused["top_source_function_frontier"]["blocked_function_count"],
                focused["top_source_function_frontier"]["blocked_function_bytes"],
            ),
            (145, 32, 9850),
        )
        self.assertEqual(
            [
                (row["function"], row["byte_length"])
                for row in focused[
                    "top_source_function_frontier"]["blocked_functions"][:3]
            ],
            [
                ("open_cfw_runtime_am145_0x005a490c", 1012),
                ("open_cfw_runtime_am145_0x005a45d0", 782),
                ("open_cfw_runtime_am145_0x005a6d10", 674),
            ],
        )
        shape = focused["top_source_function_frontier"][
            "largest_blocked_function_shape"]
        self.assertEqual(
            (
                shape["directive_byte_count"],
                shape["entry_candidate_count"],
                shape["bounded_local_return_entry_count"],
                shape["ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (1012, 1, 1, 0),
        )
        next_shape = focused["top_source_function_frontier"][
            "next_blocked_function_shape"]
        third_shape = focused["top_source_function_frontier"][
            "third_blocked_function_shape"]
        self.assertEqual(
            (
                next_shape["directive_byte_count"],
                next_shape["entry_candidate_count"],
                next_shape["bounded_local_return_entry_count"],
                next_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
                third_shape["directive_byte_count"],
                third_shape["entry_candidate_count"],
                third_shape["bounded_local_return_entry_count"],
                third_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (782, 1, 1, 0, 674, 1, 1, 0),
        )
        fourth_shape = focused["top_source_function_frontier"][
            "fourth_blocked_function_shape"]
        fifth_shape = focused["top_source_function_frontier"][
            "fifth_blocked_function_shape"]
        sixth_shape = focused["top_source_function_frontier"][
            "sixth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_byte_count"],
                fourth_shape["entry_candidate_count"],
                fourth_shape["branch_like_halfword_count"],
                fifth_shape["directive_byte_count"],
                fifth_shape["entry_candidate_count"],
                fifth_shape["branch_like_halfword_count"],
                sixth_shape["directive_byte_count"],
                sixth_shape["entry_candidate_count"],
                sixth_shape["branch_like_halfword_count"],
            ),
            (632, 3, 38, 606, 1, 29, 552, 5, 26),
        )
        seventh_shape = focused["top_source_function_frontier"][
            "seventh_blocked_function_shape"]
        eighth_shape = focused["top_source_function_frontier"][
            "eighth_blocked_function_shape"]
        ninth_shape = focused["top_source_function_frontier"][
            "ninth_blocked_function_shape"]
        tenth_shape = focused["top_source_function_frontier"][
            "tenth_blocked_function_shape"]
        self.assertEqual(
            (
                seventh_shape["directive_byte_count"],
                seventh_shape["entry_candidate_count"],
                seventh_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                eighth_shape["directive_byte_count"],
                eighth_shape["entry_candidate_count"],
                eighth_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                ninth_shape["directive_byte_count"],
                ninth_shape["entry_candidate_count"],
                tenth_shape["directive_byte_count"],
                tenth_shape["entry_candidate_count"],
            ),
            (534, 0, 0, 464, 0, 0, 390, 0, 344, 0),
        )
        eleventh_shape = focused["top_source_function_frontier"][
            "eleventh_blocked_function_shape"]
        twelfth_shape = focused["top_source_function_frontier"][
            "twelfth_blocked_function_shape"]
        thirteenth_shape = focused["top_source_function_frontier"][
            "thirteenth_blocked_function_shape"]
        fourteenth_shape = focused["top_source_function_frontier"][
            "fourteenth_blocked_function_shape"]
        fifteenth_shape = focused["top_source_function_frontier"][
            "fifteenth_blocked_function_shape"]
        self.assertEqual(
            (
                eleventh_shape["directive_byte_count"],
                eleventh_shape["entry_candidate_count"],
                eleventh_shape["unbounded_or_overlapping_entry_count"],
                twelfth_shape["directive_byte_count"],
                twelfth_shape["entry_candidate_count"],
                twelfth_shape["bounded_local_return_entry_count"],
                thirteenth_shape["directive_byte_count"],
                thirteenth_shape["entry_candidate_count"],
                fourteenth_shape["directive_byte_count"],
                fourteenth_shape["entry_candidate_count"],
                fifteenth_shape["directive_byte_count"],
                fifteenth_shape["entry_candidate_count"],
            ),
            (310, 0, 0, 302, 0, 0, 294, 0, 284, 0, 272, 1),
        )
        sixteenth_shape = focused["top_source_function_frontier"][
            "sixteenth_blocked_function_shape"]
        seventeenth_shape = focused["top_source_function_frontier"][
            "seventeenth_blocked_function_shape"]
        eighteenth_shape = focused["top_source_function_frontier"][
            "eighteenth_blocked_function_shape"]
        nineteenth_shape = focused["top_source_function_frontier"][
            "nineteenth_blocked_function_shape"]
        twentieth_shape = focused["top_source_function_frontier"][
            "twentieth_blocked_function_shape"]
        self.assertEqual(
            (
                sixteenth_shape["directive_byte_count"],
                sixteenth_shape["entry_candidate_count"],
                sixteenth_shape["branch_like_halfword_count"],
                seventeenth_shape["directive_byte_count"],
                seventeenth_shape["entry_candidate_count"],
                seventeenth_shape["branch_like_halfword_count"],
                eighteenth_shape["directive_byte_count"],
                eighteenth_shape["entry_candidate_count"],
                eighteenth_shape["branch_like_halfword_count"],
                nineteenth_shape["directive_byte_count"],
                nineteenth_shape["entry_candidate_count"],
                nineteenth_shape["return_like_count"],
                twentieth_shape["directive_byte_count"],
                twentieth_shape["entry_candidate_count"],
                twentieth_shape["branch_like_halfword_count"],
            ),
            (256, 0, 18, 250, 0, 9, 232, 2, 6, 212, 0, 0, 210, 0, 15),
        )
        twenty_first_shape = focused["top_source_function_frontier"][
            "twenty_first_blocked_function_shape"]
        twenty_second_shape = focused["top_source_function_frontier"][
            "twenty_second_blocked_function_shape"]
        twenty_third_shape = focused["top_source_function_frontier"][
            "twenty_third_blocked_function_shape"]
        twenty_fourth_shape = focused["top_source_function_frontier"][
            "twenty_fourth_blocked_function_shape"]
        twenty_fifth_shape = focused["top_source_function_frontier"][
            "twenty_fifth_blocked_function_shape"]
        twenty_sixth_shape = focused["top_source_function_frontier"][
            "twenty_sixth_blocked_function_shape"]
        twenty_seventh_shape = focused["top_source_function_frontier"][
            "twenty_seventh_blocked_function_shape"]
        twenty_eighth_shape = focused["top_source_function_frontier"][
            "twenty_eighth_blocked_function_shape"]
        twenty_ninth_shape = focused["top_source_function_frontier"][
            "twenty_ninth_blocked_function_shape"]
        thirtieth_shape = focused["top_source_function_frontier"][
            "thirtieth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_first_shape["directive_byte_count"],
                twenty_first_shape["entry_candidate_count"],
                twenty_second_shape["directive_byte_count"],
                twenty_second_shape["entry_candidate_count"],
                twenty_third_shape["directive_byte_count"],
                twenty_third_shape["bounded_local_return_entry_count"],
                twenty_fourth_shape["directive_byte_count"],
                twenty_fourth_shape["unbounded_or_overlapping_entry_count"],
                twenty_fifth_shape["directive_byte_count"],
                twenty_fifth_shape["branch_like_halfword_count"],
                twenty_sixth_shape["directive_byte_count"],
                twenty_sixth_shape["branch_like_halfword_count"],
                twenty_seventh_shape["directive_byte_count"],
                twenty_seventh_shape["branch_like_halfword_count"],
                twenty_eighth_shape["directive_byte_count"],
                twenty_eighth_shape["branch_like_halfword_count"],
                twenty_ninth_shape["directive_byte_count"],
                twenty_ninth_shape["branch_like_halfword_count"],
                thirtieth_shape["directive_byte_count"],
                thirtieth_shape["return_like_count"],
            ),
            (200, 0, 192, 0, 138, 0, 136, 0, 130, 9, 104, 3,
             82, 6, 80, 3, 66, 2, 46, 0),
        )
        next_frontier = focused["next_source_function_frontier"]
        self.assertEqual(
            (
                next_frontier["number"],
                next_frontier["blocked_function_count"],
                next_frontier["blocked_function_bytes"],
                next_frontier["largest_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["largest_blocked_function_shape"][
                    "entry_candidate_count"],
                next_frontier["next_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["next_blocked_function_shape"][
                    "entry_candidate_count"],
                next_frontier["third_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["third_blocked_function_shape"][
                    "entry_candidate_count"],
            ),
            (152, 28, 9828, 2426, 6, 1406, 14, 920, 8),
        )
        all_shapes = next_frontier["blocked_function_shapes"]
        self.assertEqual(
            (
                len(all_shapes),
                sum(shape["directive_byte_count"] for shape in all_shapes),
                sum(shape["entry_candidate_count"] for shape in all_shapes),
                sum(shape["branch_like_halfword_count"] for shape in all_shapes),
                sum(
                    1 for shape in all_shapes
                    if shape["ranked_entry_semantic_rollup"][
                        "implementation_readiness"] == "decode_only"
                ),
                all_shapes[-1]["directive_byte_count"],
                all_shapes[-1]["entry_candidate_count"],
                all_shapes[-1]["branch_like_halfword_count"],
            ),
            (28, 9828, 58, 529, 0, 14, 0, 2),
        )
        fourth_shape = next_frontier["fourth_blocked_function_shape"]
        fifth_shape = next_frontier["fifth_blocked_function_shape"]
        sixth_shape = next_frontier["sixth_blocked_function_shape"]
        seventh_shape = next_frontier["seventh_blocked_function_shape"]
        eighth_shape = next_frontier["eighth_blocked_function_shape"]
        ninth_shape = next_frontier["ninth_blocked_function_shape"]
        tenth_shape = next_frontier["tenth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_byte_count"],
                fourth_shape["entry_candidate_count"],
                fourth_shape["bounded_local_return_entry_count"],
                fourth_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
                fourth_shape["ranked_entry_pull_through_queue"][0][
                    "entry_address"],
                fifth_shape["directive_byte_count"],
                fifth_shape["entry_candidate_count"],
                fifth_shape["unbounded_or_overlapping_entry_count"],
                fifth_shape["branch_like_halfword_count"],
                fifth_shape["zero_halfword_count"],
                sixth_shape["directive_byte_count"],
                sixth_shape["entry_candidate_count"],
                sixth_shape["bounded_local_return_entry_count"],
                sixth_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
                sixth_shape["ranked_entry_pull_through_queue"][0][
                    "entry_address"],
                seventh_shape["directive_byte_count"],
                seventh_shape["entry_candidate_count"],
                seventh_shape["return_like_count"],
                seventh_shape["branch_like_halfword_count"],
                eighth_shape["directive_byte_count"],
                eighth_shape["entry_candidate_count"],
                eighth_shape["branch_like_halfword_count"],
                eighth_shape["zero_halfword_count"],
                ninth_shape["directive_byte_count"],
                ninth_shape["entry_candidate_count"],
                ninth_shape["return_like_count"],
                ninth_shape["branch_like_halfword_count"],
                ninth_shape["zero_halfword_count"],
                tenth_shape["directive_byte_count"],
                tenth_shape["entry_candidate_count"],
                tenth_shape["return_like_count"],
                tenth_shape["branch_like_halfword_count"],
            ),
            (
                632, 3, 3, 0, 0x005A67D2,
                606, 1, 1, 29, 2,
                552, 5, 5, 0, 0x005A6C52,
                534, 0, 3, 18,
                464, 0, 28, 1,
                390, 0, 1, 23, 3,
                344, 0, 0, 21,
            ),
        )
        third_frontier = focused["third_source_function_frontier"]
        third_shapes = third_frontier["blocked_function_shapes"]
        self.assertEqual(
            (
                third_frontier["number"],
                third_frontier["blocked_function_count"],
                third_frontier["blocked_function_bytes"],
                len(third_shapes),
                sum(shape["directive_byte_count"] for shape in third_shapes),
                sum(shape["entry_candidate_count"] for shape in third_shapes),
                sum(
                    shape["bounded_local_return_entry_count"]
                    for shape in third_shapes
                ),
                sum(shape["branch_like_halfword_count"] for shape in third_shapes),
                sum(
                    1 for shape in third_shapes
                    if shape["ranked_entry_semantic_rollup"][
                        "implementation_readiness"] == "decode_only"
                ),
                third_shapes[0]["directive_byte_count"],
                third_shapes[0]["entry_candidate_count"],
                third_shapes[-1]["directive_byte_count"],
                third_shapes[-1]["branch_like_halfword_count"],
            ),
            (152, 28, 9828, 28, 9828, 58, 49, 529, 0, 2426, 6, 14, 2),
        )
        source_frontiers = focused["source_function_frontiers"]
        self.assertEqual(
            (
                len(source_frontiers),
                [frontier["number"] for frontier in source_frontiers[:5]],
                sum(
                    frontier["blocked_function_bytes"]
                    for frontier in source_frontiers
                ),
                sum(
                    len(frontier["blocked_function_shapes"])
                    for frontier in source_frontiers
                ),
                sum(
                    shape["directive_byte_count"]
                    for frontier in source_frontiers
                    for shape in frontier["blocked_function_shapes"]
                ),
                sum(
                    shape["entry_candidate_count"]
                    for frontier in source_frontiers
                    for shape in frontier["blocked_function_shapes"]
                ),
                sum(
                    1
                    for frontier in source_frontiers
                    for shape in frontier["blocked_function_shapes"]
                    if shape["ranked_entry_semantic_rollup"][
                        "implementation_readiness"] == "decode_only"
                ),
            ),
            (18, [145, 152, 147, 144, 146], 118616, 486, 118616, 443, 0),
        )
        largest = quality["raw_transcript_frontier"][
            "largest_source_function_frontier"]
        self.assertEqual(
            (
                largest["number"],
                largest["source"],
                largest["blocked_function_count"],
                largest["blocked_function_bytes"],
                largest["blocked_functions"][0]["function"],
                largest["blocked_functions"][0]["byte_length"],
            ),
            (
                115,
                "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c",
                27,
                10230,
                "open_cfw_runtime_am115_0x0054692c",
                3500,
            ),
        )
        self.assertEqual(
            (
                largest["largest_function_shape"][
                    "directive_halfword_count"],
                largest["largest_function_shape"][
                    "first_prologue_halfword_index"],
                largest["largest_function_shape"]["return_like_count"],
                largest["largest_function_shape"][
                    "post_first_return_halfword_count"],
                largest["largest_function_shape"]["entry_candidate_count"],
                largest["largest_function_shape"][
                    "entry_candidates"][-1]["has_local_return"],
                largest["largest_function_shape"][
                    "bounded_local_return_entry_count"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"][
                        "entry_byte_offset"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"][
                        "bytes_through_return"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["thumb_decode"][
                        "instruction_count"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["thumb_decode"][
                        "terminal_instruction"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "kind"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "firmware_routing_status"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "gate_pointer"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "call_r0"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "call_r1"],
                [
                    row["entry_byte_offset"]
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][:4]
                ],
                [
                    row["thumb_decode_summary"]["instruction_count"]
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][:4]
                ],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][1][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][1][
                        "semantic_frontier"]["primary_literal"],
                [
                    row["semantic_frontier"]["kind"]
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][1:10]
                ],
                largest["largest_function_shape"][
                    "ranked_entry_semantic_rollup"]["semantic_model_ranks"],
                largest["largest_function_shape"][
                    "ranked_entry_semantic_rollup"][
                        "semantic_frontier_ranks"],
            ),
            (1750, 10, 11, 1632, 11, False, 10, 1238, 32, 12,
             "pop {r1, pc}", "gated_literal_call_returns_zero",
             "not_yet_routed_into_overlay", 0x200746A8, 0x0078E144,
             0x200031B4, [1238, 254, 880, 1050], [12, 61, 65, 72],
             "gated_stack_path_builder_returns_zero", 0x200031B4, [
                 "gated_stack_path_builder_returns_zero",
                 "gated_stack_path_builder_status_log_returns_zero",
                 "gated_stack_path_builder_extended_output_returns_zero",
                 "gated_dynamic_path_query_extended_output_returns_zero",
                 "gated_path_component_filter_join_returns_status",
                 "gated_dynamic_path_normalize_query_persist_returns_zero",
                 "storage_context_metrics_log_returns_zero",
                 "gated_dynamic_path_normalize_iterative_query_dump_returns_zero",
                 "gated_two_token_path_compare_update_returns_zero",
             ], [1], [2, 3, 4, 5, 6, 7, 8, 9, 10]),
        )
        next_shape = largest["next_blocked_function_shape"]
        self.assertEqual(
            (
                next_shape["directive_byte_count"],
                next_shape["entry_candidate_count"],
                next_shape["bounded_local_return_entry_count"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "entry_address"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["kind"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["argument_transform"],
                next_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                next_shape["ranked_entry_semantic_rollup"][
                    "decode_only_ranks"],
            ),
            (
                1932,
                13,
                12,
                0x00545EC4,
                "u16_argument_tail_call_wrapper",
                "uxth",
                12,
                [],
            ),
        )
        third_shape = largest["third_blocked_function_shape"]
        self.assertEqual(
            (
                third_shape["directive_byte_count"],
                third_shape["entry_candidate_count"],
                third_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                third_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                third_shape["ranked_entry_pull_through_queue"][1][
                    "semantic_frontier"]["kind"],
            ),
            (
                952,
                2,
                2,
                0,
                "retry_transaction_fill_compact_result",
            ),
        )
        fourth_shape = largest["fourth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_byte_count"],
                fourth_shape["push_like_prologue_count"],
                fourth_shape["function_semantic_frontier"]["kind"],
                fourth_shape["function_semantic_frontier"][
                    "uses_existing_stack_frame"],
            ),
            (
                520,
                0,
                "prologueless_retry_transaction_tail_fill_u16_result",
                True,
            ),
        )
        fifth_shape = largest["fifth_blocked_function_shape"]
        self.assertEqual(
            (
                fifth_shape["directive_byte_count"],
                fifth_shape["bounded_local_return_entry_count"],
                fifth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                fifth_shape["ranked_entry_pull_through_queue"][2][
                    "semantic_frontier"]["kind"],
            ),
            (
                438,
                4,
                4,
                "literal_registration_burst",
            ),
        )
        sixth_shape = largest["sixth_blocked_function_shape"]
        self.assertEqual(
            (
                sixth_shape["directive_byte_count"],
                sixth_shape["bounded_local_return_entry_count"],
                sixth_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                sixth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["action_call"],
            ),
            (
                336,
                2,
                0,
                0x004DA9BC,
            ),
        )
        seventh_shape = largest["seventh_blocked_function_shape"]
        self.assertEqual(
            (
                seventh_shape["directive_byte_count"],
                seventh_shape["entry_candidate_count"],
                seventh_shape["unbounded_or_overlapping_entry_count"],
                seventh_shape["function_semantic_frontier"][
                    "implementation_readiness"],
                seventh_shape["function_semantic_frontier"][
                    "embedded_timeout"],
            ),
            (
                334,
                1,
                1,
                "needs_split_status_query_semantics",
                0xC8,
            ),
        )
        eighth_shape = largest["eighth_blocked_function_shape"]
        self.assertEqual(
            (
                eighth_shape["directive_byte_count"],
                eighth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                eighth_shape["entry_candidates"][1]["entry_address"],
                eighth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                302,
                1,
                0x00545504,
                "needs_split_u8_status_probe_semantics",
            ),
        )
        ninth_shape = largest["ninth_blocked_function_shape"]
        self.assertEqual(
            (
                ninth_shape["directive_byte_count"],
                ninth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                ninth_shape["function_semantic_frontier"][
                    "cleanup_stack_offset"],
                ninth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                222,
                0,
                0x14,
                "needs_retry_read_status_tail_semantics",
            ),
        )
        tenth_shape = largest["tenth_blocked_function_shape"]
        self.assertEqual(
            (
                tenth_shape["directive_byte_count"],
                tenth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                tenth_shape["function_semantic_frontier"][
                    "cleanup_call"],
                tenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                206,
                0,
                0x00544660,
                "needs_u16_status_pack_tail_semantics",
            ),
        )
        eleventh_shape = largest["eleventh_blocked_function_shape"]
        self.assertEqual(
            (
                eleventh_shape["directive_byte_count"],
                eleventh_shape["return_like_count"],
                eleventh_shape["function_semantic_frontier"][
                    "caller_epilogue_stack_adjust"],
                eleventh_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                200,
                1,
                0x34,
                "needs_retry_transaction_u8_tail_semantics",
            ),
        )
        twelfth_shape = largest["twelfth_blocked_function_shape"]
        self.assertEqual(
            (
                twelfth_shape["directive_byte_count"],
                twelfth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                twelfth_shape["function_semantic_frontier"][
                    "path_append_call"],
                twelfth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                188,
                0,
                0x0052FCA0,
                "needs_dual_path_filter_join_tail_semantics",
            ),
        )
        thirteenth_shape = largest["thirteenth_blocked_function_shape"]
        self.assertEqual(
            (
                len(largest["blocked_functions"]),
                thirteenth_shape["directive_byte_count"],
                thirteenth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                thirteenth_shape["function_semantic_frontier"][
                    "transaction_start_call"],
                thirteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                27,
                182,
                0,
                0x00544462,
                "needs_transaction_setup_tail_semantics",
            ),
        )
        fourteenth_shape = largest["fourteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fourteenth_shape["directive_byte_count"],
                fourteenth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                fourteenth_shape["function_semantic_frontier"][
                    "bounded_copy_call"],
                fourteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                162,
                0,
                0x00401C04,
                "needs_dual_path_input_staging_tail_semantics",
            ),
        )
        fifteenth_shape = largest["fifteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fifteenth_shape["directive_byte_count"],
                fifteenth_shape["unbounded_or_overlapping_entry_count"],
                fifteenth_shape["function_semantic_frontier"][
                    "embedded_entry_address"],
                fifteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                106,
                1,
                0x00544D0C,
                "needs_embedded_retry_search_entry_semantics",
            ),
        )
        sixteenth_shape = largest["sixteenth_blocked_function_shape"]
        self.assertEqual(
            (
                sixteenth_shape["directive_byte_count"],
                sixteenth_shape["first_return_halfword_index"],
                sixteenth_shape["function_semantic_frontier"][
                    "terminal_return_halfword_index"],
                sixteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                106,
                42,
                42,
                "needs_u8_status_debug_tail_semantics",
            ),
        )
        seventeenth_shape = largest["seventeenth_blocked_function_shape"]
        self.assertEqual(
            (
                seventeenth_shape["directive_byte_count"],
                seventeenth_shape["unbounded_or_overlapping_entry_count"],
                seventeenth_shape["function_semantic_frontier"][
                    "option_stack_offset"],
                seventeenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                100,
                1,
                0x10,
                "needs_embedded_retry_option_initializer_semantics",
            ),
        )
        eighteenth_shape = largest["eighteenth_blocked_function_shape"]
        self.assertEqual(
            (
                eighteenth_shape["directive_byte_count"],
                eighteenth_shape["ranked_entry_semantic_rollup"][
                    "ranked_entry_count"],
                eighteenth_shape["function_semantic_frontier"][
                    "success_tail_entry"],
                eighteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                96,
                0,
                0x0054566E,
                "needs_u16_status_retry_search_tail_semantics",
            ),
        )
        nineteenth_shape = largest["nineteenth_blocked_function_shape"]
        self.assertEqual(
            (
                nineteenth_shape["directive_byte_count"],
                nineteenth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                nineteenth_shape["function_semantic_frontier"][
                    "wrapper_call_target"],
                nineteenth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                80,
                1,
                0x00545C74,
                "needs_vfp_compare_wrapper_and_body_semantics",
            ),
        )
        twentieth_shape = largest["twentieth_blocked_function_shape"]
        self.assertEqual(
            (
                twentieth_shape["directive_byte_count"],
                twentieth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twentieth_shape["function_semantic_frontier"][
                    "tail_debug_call"],
                twentieth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                58,
                0,
                0x00404EBE,
                "needs_boundary_reconciliation_before_crc_or_status_semantics",
            ),
        )
        twenty_first_shape = largest["twenty_first_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_first_shape["directive_byte_count"],
                twenty_first_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_first_shape["function_semantic_frontier"][
                    "debug_emit_call"],
                twenty_first_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                50,
                0,
                0x00404EBE,
                "needs_four_stage_debug_log_tail_semantics",
            ),
        )
        twenty_second_shape = largest["twenty_second_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_second_shape["directive_byte_count"],
                twenty_second_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_second_shape["function_semantic_frontier"][
                    "debug_emit_call"],
                twenty_second_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                40,
                0,
                0x0043CE9E,
                "needs_compass_debug_tail_boundary_semantics",
            ),
        )
        twenty_third_shape = largest["twenty_third_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_third_shape["directive_byte_count"],
                twenty_third_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_third_shape["function_semantic_frontier"][
                    "debug_gate_call"],
                twenty_third_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                36,
                0,
                0x0043D0CE,
                "needs_condition_flag_debug_emit_tail_semantics",
            ),
        )
        twenty_fourth_shape = largest["twenty_fourth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fourth_shape["directive_byte_count"],
                twenty_fourth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_fourth_shape["function_semantic_frontier"][
                    "authenticated_decompile_kind"],
                twenty_fourth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                32,
                0,
                "two_byte_affine_mixer_no_callees",
                "needs_status_query_tail_boundary_reconciliation",
            ),
        )
        twenty_fifth_shape = largest["twenty_fifth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fifth_shape["directive_byte_count"],
                twenty_fifth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_fifth_shape["function_semantic_frontier"][
                    "embedded_entry_address"],
                twenty_fifth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                30,
                0,
                0x005455E0,
                "needs_two_call_entry_boundary_reconciliation",
            ),
        )
        twenty_sixth_shape = largest["twenty_sixth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_sixth_shape["directive_byte_count"],
                twenty_sixth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_sixth_shape["function_semantic_frontier"][
                    "authenticated_decompile_call"],
                twenty_sixth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                12,
                0,
                0x0044BDEA,
                "needs_opacity_debug_prefix_boundary_reconciliation",
            ),
        )
        twenty_seventh_shape = largest["twenty_seventh_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_seventh_shape["directive_byte_count"],
                twenty_seventh_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                twenty_seventh_shape["function_semantic_frontier"][
                    "tail_branch_target"],
                twenty_seventh_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                10,
                0,
                0x00544C96,
                "needs_retry_service_tail_branch_semantics",
            ),
        )
        raw_gate = self.report["gate_raw_transcript_blockers"]
        self.assertEqual(raw_gate["raw_transcript_source_count"], 102)
        self.assertEqual(raw_gate["raw_transcript_bytes"], 584954)
        self.assertEqual(raw_gate["source_path_sha256"],
                         quality["public_unrouted_raw_instruction_source_path_sha256"])
        self.assertEqual(
            raw_gate["mixed_boundary_reason_counts"][
                "linear_raw_instruction_text_still_needs_source_model"],
            90,
        )
        untracked = self.report["untracked_overlay_inputs"]
        self.assertEqual(untracked["raw_bearing_input_count"], 0)
        self.assertEqual(untracked["non_raw_input_count"], 0)
        self.assertEqual(len(untracked["raw_bearing_am_helper_ranges"]), 0)
        self.assertEqual(len(untracked["non_raw_am_helper_ranges"]), 0)
        self.assertEqual(
            [
                (
                    row["source"],
                    row["inst_directive_bytes"],
                    row["family"],
                )
                for row in untracked["largest_raw_bearing_inputs"][:3]
            ],
            [],
        )

    def test_rollup_matches_am_audits(self) -> None:
        audits = self.report["am_blocker_audits"]
        self.assertEqual(audits["linear_raw"]["byte_count"], 69030)
        self.assertEqual(audits["branch_targets"]["site_count"], 5597)
        self.assertEqual(audits["pc_boundary"]["pc_reference_count"], 2001)
        self.assertEqual(audits["vector_it"]["blocker_count"], 368)

    def test_next_pull_through_frontier_is_ranked(self) -> None:
        frontier = self.report["next_pull_through_frontier"]
        self.assertFalse(frontier["release_authorized"])
        self.assertTrue(frontier["macos_build_proven_elsewhere"])
        self.assertEqual(
            frontier["primary_global_gate"],
            {
                "kind": "source_ownership_quality",
                "blocking": True,
                "raw_transcript_source_count": 102,
                "raw_transcript_bytes": 584954,
                "source_path_sha256": (
                    "d778c1ad00f7390a619b26a5064709ae26697d7aa80be883e57dd4a363dfecfb"
                ),
                "exit_criteria": [
                    "Replace public raw instruction transcript sources with source-owned code models or remove them from production routing.",
                    "Reduce public_unrouted_raw_instruction_transcript_files and public_unrouted_raw_instruction_transcript_bytes to zero.",
                    "Drive source_owned_bytes_currently_overstated back to zero while preserving macOS apple-clang source-only verification.",
                ],
            },
        )
        self.assertEqual(
            [
                (row["scope"], row["blocking_bytes"])
                for row in frontier["component_priority"]
            ],
            [
                ("apollo_main", 3032198),
                ("codec", 326000),
                ("ble_em9305", 210584),
                ("apollo_bootloader", 81187),
                ("case", 55752),
                ("touch", 33952),
            ],
        )
        apollo = frontier["component_priority"][0]
        self.assertEqual(apollo["scope"], "apollo_main")
        self.assertEqual(
            (
                apollo["source_build_route"]["manifest"],
                apollo["source_build_route"]["provider_path"],
                apollo["source_build_route"]["provider_size"],
                apollo["source_build_route"]["provider_sha256"],
                apollo["source_build_route"]["toolchain_profile"],
                apollo["source_build_route"]["source_owned_bytes"],
                apollo["source_build_route"]["opaque_base_bytes"],
            ),
            (
                "manifests/g2-2.2.6.10-core-source.json",
                "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
                3956672,
                "97c0f4191de23eb9a46ea25c963a53dff57f8084c422c33ee7f07e486eebd8c9",
                "apple-clang",
                530980,
                3030368,
            ),
        )
        codec = frontier["component_priority"][1]
        self.assertEqual(codec["scope"], "codec")
        self.assertIn(
            "Provide source-owned or redistributable exact-provider implementations for all 11 GX8002 typed external spans.",
            codec["exit_criteria"],
        )
        self.assertEqual(codec["typed_external_span_count"], 11)
        self.assertEqual(
            codec["external_provider_bytes_by_class"],
            {
                "opaque_executable": 190912,
                "opaque_npu_commands": 9164,
                "opaque_runtime_data": 5124,
                "proprietary_model_data": 120800,
            },
        )
        self.assertEqual(
            (
                codec["source_only_macos_route"]["manifest"],
                codec["source_only_macos_route"]["provider_path"],
                codec["source_only_macos_route"]["provider_size"],
                codec["source_only_macos_route"]["provider_sha256"],
                codec["source_only_macos_route"]["toolchain_profile"],
                codec["source_only_macos_route"]["source_only"],
                codec["source_only_macos_route"]["hardware_qualified"],
            ),
            (
                "manifests/g2-2.2.6.10-source-only.json",
                "build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin",
                326092,
                "ea1228240563deb21e2093793c50295bfe76e9a0c12cd77963ae581d7c270956",
                "apple-clang",
                False,
                False,
            ),
        )
        ble = frontier["component_priority"][2]
        self.assertEqual(ble["scope"], "ble_em9305")
        self.assertEqual(
            ble["residual_readiness"],
            {
                "concrete_source_available": {"bytes": 1240, "spans": 23},
                "typed_unsupported_external_boundary": {
                    "bytes": 8348,
                    "spans": 25,
                },
                "unavailable_proprietary_controller_code": {
                    "bytes": 24070,
                    "spans": 127,
                },
            },
        )
        self.assertEqual(
            (
                ble["largest_residual_blocker"]["start"],
                ble["largest_residual_blocker"]["size"],
                ble["largest_residual_blocker"]["decision"],
            ),
            (3315848, 3126, "six_entry_slave_connection_provider_boundary"),
        )
        self.assertEqual(
            (
                ble["source_build_route"]["manifest"],
                ble["source_build_route"]["provider_path"],
                ble["source_build_route"]["provider_size"],
                ble["source_build_route"]["provider_sha256"],
                ble["source_build_route"]["package_toolchain_profile"],
                ble["source_build_route"]["production_routed"],
                ble["source_build_route"]["accounting"][
                    "typed_retained_or_external_bytes"],
            ),
            (
                "manifests/g2-2.2.6.10-core-source.json",
                "components/em9305/source_overlay/build/firmware_ble_em9305.bin",
                212984,
                "56694060c0d2761c2004581d0cec97cdb8642c1ff44675194d05d605bf8dd9c7",
                "apple-clang",
                True,
                210584,
            ),
        )
        boot = frontier["component_priority"][3]
        self.assertEqual(boot["scope"], "apollo_bootloader")
        self.assertEqual(
            boot["retained_official_bytes_by_family"][
                "easylogger_replacement_frontier"],
            31870,
        )
        self.assertEqual(
            (
                boot["largest_retained_interval"]["file_offset"],
                boot["largest_retained_interval"]["size"],
                boot["largest_retained_interval"]["family"],
                boot["largest_retained_interval"]["name"],
            ),
            (
                3638,
                18266,
                "redirect_init_frontier",
                "opaque_before_replace_bootloader_redirect_init",
            ),
        )
        self.assertEqual(
            (
                boot["source_build_route"]["manifest"],
                boot["source_build_route"]["provider_path"],
                boot["source_build_route"]["provider_size"],
                boot["source_build_route"]["provider_sha256"],
                boot["source_build_route"]["toolchain_profile"],
                boot["source_build_route"]["source_owned_bytes"],
                boot["source_build_route"]["opaque_base_bytes"],
            ),
            (
                "manifests/g2-2.2.6.10-core-source.json",
                "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
                163840,
                "696a6bafaea197c8a6237a626bdee3b2742a1b83a39b2bd0a2f12c01c6c6b4f3",
                "apple-clang",
                65807,
                81187,
            ),
        )
        case = frontier["component_priority"][4]
        self.assertEqual(case["scope"], "case")
        self.assertEqual(
            case["whole_blob_bucket_bytes"],
            {
                "generated_transport_fill": 32,
                "project_source_candidate": 14886,
                "still_unclassified": 0,
                "typed_external_or_unsupported": 40866,
            },
        )
        self.assertEqual(
            case["candidate_admission_blocker_class"],
            "hardware-dependent-board-routing",
        )
        self.assertEqual(
            case["gap_classification_counts"],
            {
                "typed_unsupported_interfunction_code_or_data_boundary": 198,
                "typed_zero_alignment_or_data": 31,
            },
        )
        self.assertEqual(
            (
                case["source_only_macos_route"]["manifest"],
                case["source_only_macos_route"]["provider_path"],
                case["source_only_macos_route"]["provider_size"],
                case["source_only_macos_route"]["provider_sha256"],
                case["source_only_macos_route"]["toolchain_profile"],
                case["source_only_macos_route"]["software_package_complete"],
                case["source_only_macos_route"]["production_routed"],
            ),
            (
                "manifests/g2-2.2.6.10-source-only.json",
                "build/case-source-image/firmware_box.bin",
                18948,
                "5af2623dba3e4316f03a368510be02b2cfb5aace7331030110472b375d2b5fa8",
                "apple-clang",
                True,
                False,
            ),
        )
        touch = frontier["component_priority"][5]
        self.assertEqual(touch["scope"], "touch")
        self.assertIn(
            "Resolve the touch resident ABI and physical board-service routing.",
            touch["exit_criteria"],
        )
        self.assertFalse(touch["resident_abi_available"])
        self.assertEqual(
            touch["candidate_admission_blocker_class"],
            "hardware-dependent-resident-abi",
        )
        self.assertEqual(
            touch["whole_blob_bucket_bytes"],
            {
                "generated_transport_fill": 512,
                "project_source_candidate": 14510,
                "still_unclassified": 0,
                "typed_external_or_unsupported": 19442,
            },
        )
        self.assertEqual(
            {
                key: touch["typed_physical_bucket_bytes"][key]
                for key in (
                    "typed_code_capsense_cat2_mixed_provider",
                    "typed_code_owner_unresolved",
                    "typed_noncode_config_and_tables",
                )
            },
            {
                "typed_code_capsense_cat2_mixed_provider": 7000,
                "typed_code_owner_unresolved": 6686,
                "typed_noncode_config_and_tables": 1756,
            },
        )
        self.assertEqual(
            (
                touch["source_only_macos_route"]["manifest"],
                touch["source_only_macos_route"]["provider_path"],
                touch["source_only_macos_route"]["provider_size"],
                touch["source_only_macos_route"]["provider_sha256"],
                touch["source_only_macos_route"]["toolchain_profile"],
                touch["source_only_macos_route"]["software_package_complete"],
                touch["source_only_macos_route"]["production_routed"],
            ),
            (
                "manifests/g2-2.2.6.10-source-only.json",
                "build/touch-source-image/firmware_touch.bin",
                15516,
                "128e8e2e6321b5bf3515317fe1935927afd0ec1dcd3be0e1e70f38a6a70c74ac",
                "apple-clang",
                True,
                False,
            ),
        )
        self.assertEqual(
            frontier["apollo_main_priority"]["top_mixed_boundary_classes"][0],
            {
                "scope": "apollo_main",
                "kind": "am_mixed_boundary_class",
                "class": "linear:pc_relative_or_pc_operand_needs_boundary_model",
                "blocking_bytes": 143958,
                "function_count": 639,
            },
        )
        self.assertEqual(
            [
                (row["class"], row["blocking_bytes"])
                for row in frontier["apollo_main_priority"][
                    "audited_boundary_surfaces"]
            ],
            [
                ("pc_boundary", 340642),
                ("vector_it", 170890),
                ("linear_raw", 69030),
                ("branch_targets", 65036),
            ],
        )
        am115 = frontier["apollo_am115_pullthrough_candidate_frontier"]
        self.assertEqual(
            {
                key: am115[key]
                for key in (
                    "available",
                    "manifest",
                    "source",
                    "candidate_addresses",
                    "target_compile_verified",
                    "toolchain_profile",
                    "object_sha256",
                    "symbol_count",
                    "undefined_symbol_count",
                    "relocation_count",
                    "firmware_routing_status",
                )
            },
            {
                "available": True,
                "manifest": (
                    "tools/manifests/"
                    "g2-apollo-am115-pullthrough-candidate.json"
                ),
                "source": (
                    "components/apollo_main/core_overlay/"
                    "runtime_liblc3_am115_semantic_model.c"
                ),
                "candidate_addresses": [
                    "0x005455c6",
                    "0x00545ec4",
                    "0x00546e02",
                ],
                "target_compile_verified": True,
                "toolchain_profile": "apple-clang",
                "object_sha256": (
                    "b4c524b0194a0f9781ebc2916cde7067c4dc78e83a7010579800094c00f8be71"
                ),
                "symbol_count": 3,
                "undefined_symbol_count": 0,
                "relocation_count": 3,
                "firmware_routing_status": "not_yet_routed_into_overlay",
            },
        )
        am145 = frontier["apollo_am145_pullthrough_candidate_frontier"]
        self.assertEqual(
            {
                key: am145[key]
                for key in (
                    "available",
                    "manifest",
                    "source",
                    "candidate_addresses",
                    "target_compile_verified",
                    "toolchain_profile",
                    "object_sha256",
                    "symbol_count",
                    "undefined_symbol_count",
                    "relocation_count",
                    "firmware_routing_status",
                )
            },
            {
                "available": True,
                "manifest": (
                    "tools/manifests/"
                    "g2-apollo-am145-pullthrough-candidate.json"
                ),
                "source": (
                    "components/apollo_main/core_overlay/"
                    "runtime_liblc3_am145_semantic_model.c"
                ),
                "candidate_addresses": [
                    "0x005a340c",
                    "0x005a34ca",
                    "0x005a35a4",
                    "0x005a36ac",
                    "0x005a3798",
                    "0x005a3980",
                    "0x005a3a10",
                    "0x005a3ab0",
                    "0x005a3bcc",
                    "0x005a3cc6",
                    "0x005a3e24",
                    "0x005a3fe8",
                    "0x005a40ca",
                    "0x005a4a66",
                    "0x005a4b36",
                    "0x005a4802",
                    "0x005a487a",
                    "0x005a490c",
                    "0x005a63c8",
                    "0x005a6596",
                    "0x005a659a",
                    "0x005a65a2",
                    "0x005a65b0",
                    "0x005a66cc",
                    "0x005a674a",
                    "0x005a6c52",
                    "0x005a6c5e",
                    "0x005a6c7c",
                    "0x005a6c94",
                    "0x005a6ca2",
                    "0x005a6cb0",
                    "0x005a6d10",
                    "0x005a67d2",
                    "0x005a6822",
                    "0x005a6e34",
                    "0x005a6e4a",
                    "0x005a6eb6",
                    "0x005a6f5c",
                ],
                "target_compile_verified": True,
                "toolchain_profile": "apple-clang",
                "object_sha256": (
                    "a7c99942b924a6f9b202d226b9a88431e45c2d9e9c39af88c6fa2be16e93c3d3"
                ),
                "symbol_count": 38,
                "undefined_symbol_count": 0,
                "relocation_count": 38,
                "firmware_routing_status": "not_yet_routed_into_overlay",
            },
        )
        hot_targets = frontier["apollo_retained_hot_target_frontier"]
        self.assertTrue(hot_targets["available"])
        self.assertEqual(
            hot_targets["manifest"],
            "tools/manifests/g2-apollo-retained-hot-targets.json",
        )
        self.assertEqual(hot_targets["hot_target_count"], 10)
        self.assertEqual(
            hot_targets["semantic_status"],
            {
                "contract_complete": True,
                "contract_count": 6,
                "contract_kind_counts": {
                    "call_shim_to_retained_helper": 2,
                    "integer_affine_index_update": 1,
                    "squared_delta_accumulator": 1,
                    "stack_parabolic_compare_branch": 1,
                    "threshold_offset_branch": 1,
                },
                "firmware_routing_status_counts": {
                    "not_yet_routed_into_overlay": 6,
                },
            },
        )
        self.assertEqual(
            hot_targets["target_shape_counts"],
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
                    row["target_shape"],
                    row["first_instruction"],
                )
                for row in hot_targets["top_targets"][:3]
            ],
            [
                (
                    19,
                    0x004EC718,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29264,
                    "direct_subroutine_entry",
                    "mov r0, sl",
                ),
                (
                    16,
                    0x004EC774,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29356,
                    "direct_subroutine_entry",
                    "mov sb, r0",
                ),
                (
                    12,
                    0x0059C766,
                    (
                        "opaque_between_ring_buffer_and_"
                        "pb_translate_split_0016025c_00165264"
                    ),
                    17706,
                    "nondecoding_branch_target",
                    None,
                ),
            ],
        )
        self.assertEqual(
            [
                (
                    row["count"],
                    row["target_address"],
                    row["region"],
                    row["offset_in_region"],
                    row["first_instruction"],
                )
                for row in hot_targets["direct_subroutine_frontier"][:3]
            ],
            [
                (
                    19,
                    0x004EC718,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29264,
                    "mov r0, sl",
                ),
                (
                    16,
                    0x004EC774,
                    "opaque_after_pb_even_ai_before_ring_battery_service",
                    29356,
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
                    "sub.w lr, sl, ip",
                ),
            ],
        )
        self.assertEqual(
            [
                (
                    row["priority"],
                    row["target_address"],
                    row["dependency_class"],
                    row["external_dependency_count"],
                    row["count"],
                )
                for row in hot_targets["source_pull_through_queue"][:3]
            ],
            [
                (1, 0x0059A312, "isolated_window", 0, 4),
                (2, 0x0059A32E, "isolated_window", 0, 4),
                (3, 0x0059C060, "same_retained_interval_only", 0, 7),
            ],
        )
        self.assertEqual(
            (
                hot_targets["source_pull_through_clusters"][0]["priority"],
                hot_targets["source_pull_through_clusters"][0]["start_address"],
                hot_targets["source_pull_through_clusters"][0]["end_address"],
                hot_targets["source_pull_through_clusters"][0]["byte_length"],
                hot_targets["source_pull_through_clusters"][0][
                    "dependency_class"],
                hot_targets["source_pull_through_clusters"][0][
                    "total_call_site_count"],
                [
                    target["target_address"]
                    for target in hot_targets[
                        "source_pull_through_clusters"][0]["targets"]
                ],
            ),
            (
                1,
                0x0059A312,
                0x0059A3A6,
                148,
                "isolated_window",
                8,
                [0x0059A312, 0x0059A32E],
            ),
        )
        self.assertEqual(
            (
                hot_targets["source_pull_through_clusters"][0][
                    "instruction_count"],
                hot_targets["source_pull_through_clusters"][0][
                    "instructions"][0]["instruction"],
                hot_targets["source_pull_through_clusters"][0][
                    "instructions"][-2]["instruction"],
                hot_targets["source_pull_through_clusters"][0][
                    "instructions"][-1]["instruction"],
                hot_targets["source_pull_through_clusters"][0][
                    "instructions"][-1]["target_address"],
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
                hot_targets["source_pull_through_clusters"][0][
                    "source_recovery_status"]["status"],
                hot_targets["source_pull_through_clusters"][0][
                    "source_recovery_status"]["current_representation"],
                hot_targets["source_pull_through_clusters"][0][
                    "source_recovery_status"]["decoded"],
                hot_targets["source_pull_through_clusters"][0][
                    "source_recovery_status"]["byte_length"],
                [
                    (
                        row["target_address"],
                        row["bounded_span_byte_length"],
                        row["call_site_count"],
                    )
                    for row in hot_targets[
                        "source_pull_through_clusters"][0][
                            "source_recovery_status"]["entrypoints"]
                ],
            ),
            (
                "requires_c_pull_through",
                "retained_exact_helper_bytes",
                True,
                148,
                [(0x0059A312, 148, 4), (0x0059A32E, 120, 4)],
            ),
        )
        self.assertEqual(
            {
                key: hot_targets["source_pull_through_clusters"][0][
                    "feature_summary"][key]
                for key in ("memory_reads", "memory_writes")
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
            },
        )
        self.assertEqual(
            (
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["kind"],
                [
                    (
                        lane["value_offset"],
                        lane["coefficient_offset"],
                        lane["stack_zero_offset"],
                    )
                    for lane in hot_targets[
                        "source_pull_through_clusters"][0][
                            "arithmetic_motif"]["lanes"]
                ],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["terminal_compare"],
            ),
            (
                "squared_delta_accumulator",
                [(180, 52, 316), (184, 56, 320), (188, 60, 324)],
                {
                    "instruction": "cmp r2, #0xa",
                    "branch_instruction": "bge #0x59a45c",
                    "branch_target": 0x0059A45C,
                },
            ),
        )
        self.assertEqual(
            (
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"][
                        "c_translation_status"],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"]["operations"][-1],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"]["abi_contract"][
                        "branch_condition"],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"]["abi_validation"][
                        "matches_decoded_features"],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"]["abi_validation"][
                        "observed_s16_write_count"],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"][
                        "reference_evidence"]["firmware_routing_status"],
                hot_targets["source_pull_through_clusters"][0][
                    "arithmetic_motif"]["source_model"][
                        "reference_evidence"]["overlay_source_listed"],
            ),
            (
                "semantic_model_ready_requires_register_abi_mapping",
                "branch to 0x59a45c when residual >= 10",
                {
                    "residual_register": "r2",
                    "comparison": "r2 >= 10",
                    "target_address": 0x0059A45C,
                },
                True,
                4,
                "not_yet_routed_into_overlay",
                False,
            ),
        )
        focused = frontier["apollo_main_priority"][
            "focused_source_function_frontier"]
        largest = frontier["apollo_main_priority"][
            "largest_raw_source_function_frontier"]
        self.assertEqual(
            (
                largest["number"],
                largest["source"],
                largest["inst_directive_bytes"],
                largest["blocked_function_count"],
                largest["blocked_function_bytes"],
                largest["blocked_functions"][0]["function"],
                largest["blocked_functions"][0]["byte_length"],
                largest["largest_function_shape"]["entry_candidate_count"],
                largest["largest_function_shape"]["entry_candidates"][0][
                    "entry_byte_offset"],
                largest["largest_function_shape"]["entry_candidates"][-1][
                    "entry_byte_offset"],
                largest["largest_function_shape"]["entry_candidates"][-1][
                    "has_local_return"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"][
                        "entry_byte_offset"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"][
                        "bytes_through_return"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["thumb_decode"][
                        "call_targets"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["thumb_decode"][
                        "terminal_instruction"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["semantic_model"][
                        "function"],
                largest["largest_function_shape"][
                    "next_entry_pull_through_candidate"]["thumb_decode"][
                        "literal_pool_references"][0]["word"],
                [
                    (row["rank"], row["bytes_through_return"])
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][:3]
                ],
                [
                    row["thumb_decode_summary"]["terminal_instruction"]
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][:3]
                ],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][1][
                        "semantic_frontier"]["overflow_log_literal"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][3][
                        "semantic_frontier"]["fallback_call"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][3][
                        "semantic_frontier"]["extra_output_buffer_offset"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][4][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][4][
                        "semantic_frontier"]["query_success_call"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][5][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][5][
                        "semantic_frontier"]["overflow_return_value"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][6][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][6][
                        "semantic_frontier"]["normalizer_call"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][7][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][7][
                        "semantic_frontier"]["context_pointer"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][8][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][8][
                        "semantic_frontier"]["query_record_call"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][9][
                        "semantic_frontier"]["kind"],
                largest["largest_function_shape"][
                    "ranked_entry_pull_through_queue"][9][
                        "semantic_frontier"]["query_update_call"],
                largest["largest_function_shape"][
                    "ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (
                115,
                "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c",
                10230,
                27,
                10230,
                "open_cfw_runtime_am115_0x0054692c",
                3500,
                11,
                20,
                3456,
                False,
                1238,
                32,
                ["#0x43b40e"],
                "pop {r1, pc}",
                "open_cfw_am115_0x546e02_semantic_model",
                0x200746A8,
                [(1, 32), (2, 158), (3, 170)],
                [
                    "pop {r1, pc}",
                    "pop {r4, r5, r6, pc}",
                    "pop {r4, r5, r6, pc}",
                ],
                0x0078272C,
                0x00497AF0,
                0x104,
                "gated_dynamic_path_query_extended_output_returns_zero",
                0x00497B60,
                "gated_path_component_filter_join_returns_status",
                -1,
                "gated_dynamic_path_normalize_query_persist_returns_zero",
                0x00546AC8,
                "storage_context_metrics_log_returns_zero",
                0x20074ABC,
                "gated_dynamic_path_normalize_iterative_query_dump_returns_zero",
                0x00497B60,
                "gated_two_token_path_compare_update_returns_zero",
                0x00497AA0,
                0,
            ),
        )
        self.assertEqual(
            (
                focused["number"],
                focused["source"],
                focused["inst_directive_bytes"],
                focused["blocked_function_count"],
                focused["blocked_function_bytes"],
            ),
            (
                145,
                "components/apollo_main/core_overlay/runtime_liblc3_am145_helpers.c",
                9850,
                32,
                9850,
            ),
        )
        self.assertEqual(
            focused["unresolved_source_field_path_counts"],
            {},
        )
        self.assertEqual(
            focused["branch_target_owner_counts"],
            {
                "apollo_main:apollo_opaque_after_kvdb_time:official_blob": 1,
                (
                    "apollo_main:opaque_after_cordio_atts_write_01_split_"
                    "0016e278-00173f18:official_blob"
                ): 82,
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob"
                ): 31,
                (
                    "apollo_main:opaque_between_pb_translate_and_at_buzzer_"
                    "split_00167b00_0016cfc4:official_blob"
                ): 138,
                "apollo_main:watchdog_literal_pool_compatibility:official_blob": 1,
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite"
                ): 1,
                "unresolved:indirect_or_no_imm": 14,
            },
        )
        self.assertEqual(
            [
                (row["owner"], row["count"])
                for row in focused["branch_target_owner_frontier"]
            ],
            [
                (
                    "apollo_main:opaque_between_pb_translate_and_at_buzzer_"
                    "split_00167b00_0016cfc4:official_blob",
                    138,
                ),
                (
                    "apollo_main:opaque_after_cordio_atts_write_01_split_"
                    "0016e278-00173f18:official_blob",
                    82,
                ),
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob",
                    31,
                ),
                ("unresolved:indirect_or_no_imm", 14),
                ("apollo_main:apollo_opaque_after_kvdb_time:official_blob", 1),
                ("apollo_main:watchdog_literal_pool_compatibility:official_blob", 1),
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite",
                    1,
                ),
            ],
        )
        self.assertEqual(
            {
                key: focused["branch_target_owner_frontier"][0][key]
                for key in (
                    "component",
                    "region",
                    "address_status",
                    "file_offset",
                    "end_file_offset",
                    "target_address",
                    "end_target_address",
                    "size",
                    "output",
                )
            },
            {
                "component": "apollo_main",
                "region": "opaque_between_pb_translate_and_at_buzzer_split_00167b00_0016cfc4",
                "address_status": "official_blob",
                "file_offset": 1473280,
                "end_file_offset": 1494980,
                "target_address": 5896928,
                "end_target_address": 5918628,
                "size": 21700,
                "output": "apollo510b/liblc3_service_audio-retained-00167b00-0016cfc4.bin",
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
                for row in focused["branch_target_site_frontier"][:5]
            ],
            [
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob",
                    5164964,
                    31452,
                    16,
                ),
                (
                    "apollo_main:opaque_between_pb_translate_and_at_buzzer_"
                    "split_00167b00_0016cfc4:official_blob",
                    5911732,
                    14804,
                    8,
                ),
                (
                    "apollo_main:opaque_between_pb_translate_and_at_buzzer_"
                    "split_00167b00_0016cfc4:official_blob",
                    5917468,
                    20540,
                    6,
                ),
                (
                    "apollo_main:opaque_between_pb_translate_and_at_buzzer_"
                    "split_00167b00_0016cfc4:official_blob",
                    5917252,
                    20324,
                    5,
                ),
                (
                    "apollo_main:opaque_after_cordio_atts_write_01_split_"
                    "0016e278-00173f18:official_blob",
                    5926706,
                    3290,
                    4,
                ),
            ],
        )
        self.assertEqual(
            focused["branch_target_site_frontier"][0][
                "call_site_examples"][:3],
            [
                {
                    "offset": 582,
                    "instruction": "bl #0x4ecfa4",
                    "target_offset": -751976,
                    "target_relation": "outside_function",
                },
                {
                    "offset": 634,
                    "instruction": "bl #0x4ecfa4",
                    "target_offset": -751976,
                    "target_relation": "outside_function",
                },
                {
                    "offset": 658,
                    "instruction": "bl #0x4ecfa4",
                    "target_offset": -751976,
                    "target_relation": "outside_function",
                },
            ],
        )
        first_function = focused["blocked_functions"][0]
        self.assertEqual(
            (
                first_function["function"],
                first_function["byte_length"],
                first_function["pc_reference_count"],
                first_function["pc_reference_relation_counts"],
                first_function["return_terminated_segment_count"],
                first_function["it_offsets"],
            ),
            (
                "open_cfw_runtime_am145_0x005a490c",
                1012,
                1,
                {"pc_control_operand": 1},
                2,
                [],
            ),
        )
        self.assertEqual(
            [
                {
                    key: row[key]
                    for key in ("start_offset", "end_offset", "byte_length")
                }
                for row in first_function[
                    "largest_return_terminated_segments"][:3]
            ],
            [
                {"start_offset": 302, "end_offset": 934, "byte_length": 632},
                {"start_offset": 1456, "end_offset": 1986, "byte_length": 530},
                {"start_offset": 0, "end_offset": 302, "byte_length": 302},
            ],
        )
        self.assertEqual(
            first_function["unresolved_source_field_path_counts"],
            {
                "r0+0x224->+0x4": 1,
                "r0+0x224->+0xc": 1,
            },
        )
        self.assertEqual(
            first_function["branch_target_owner_counts"],
            {
                (
                    "apollo_main:opaque_after_iar_runtime_before_"
                    "easylogger_control_split_00004fb0_00005280_split_"
                    "000050e8_00005280:official_blob"
                ): 1,
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob"
                ): 22,
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob"
                ): 109,
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite"
                ): 7,
                "unresolved:indirect_or_no_imm": 11,
            },
        )
        self.assertEqual(
            [
                (row["owner"], row["count"])
                for row in first_function["branch_target_owner_frontier"]
            ],
            [
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    109,
                ),
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob",
                    22,
                ),
                ("unresolved:indirect_or_no_imm", 11),
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite",
                    7,
                ),
                (
                    "apollo_main:opaque_after_iar_runtime_before_"
                    "easylogger_control_split_00004fb0_00005280_split_"
                    "000050e8_00005280:official_blob",
                    1,
                ),
            ],
        )
        self.assertEqual(
            (
                first_function["branch_target_owner_frontier"][0]["file_offset"],
                first_function["branch_target_owner_frontier"][0][
                    "end_file_offset"],
                first_function["branch_target_owner_frontier"][0]["size"],
            ),
            (1442396, 1462884, 20488),
        )
        self.assertEqual(
            [
                (
                    row["owner"],
                    row["target_address"],
                    row["target_owner"]["offset_in_region"],
                    row["count"],
                )
                for row in first_function["branch_target_site_frontier"][:4]
            ],
            [
                (
                    "apollo_main:opaque_after_pb_even_ai_before_"
                    "ring_battery_service:official_blob",
                    5162868,
                    29356,
                    14,
                ),
                (
                    "protected_region:ambiq_secure_bootloader:"
                    "not_present_in_evenota_do_not_overwrite",
                    4210948,
                    16644,
                    5,
                ),
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    5876630,
                    10586,
                    4,
                ),
                (
                    "apollo_main:opaque_between_ring_buffer_and_"
                    "pb_translate_split_0016025c_00165264:official_blob",
                    5878338,
                    12294,
                    4,
                ),
            ],
        )
        self.assertEqual(
            first_function["branch_target_site_frontier"][0][
                "call_site_examples"][:3],
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
                {
                    "offset": 718,
                    "instruction": "bl #0x4ec774",
                    "target_offset": -713488,
                    "target_relation": "outside_function",
                },
            ],
        )
        self.assertEqual(
            first_function["largest_return_terminated_segments"][0][
                "branch_site_counts"],
            {
                "branch:inside_function": 26,
                "call:indirect_or_no_imm": 2,
                "call:inside_function": 6,
                "call:outside_function": 14,
            },
        )
        self.assertEqual(
            first_function["largest_return_terminated_segments"][0][
                "branch_target_owner_counts"],
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
            first_function["largest_return_terminated_segments"][0][
                "unresolved_source_field_path_counts"],
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
                for row in first_function[
                    "largest_return_terminated_segments"][0][
                        "unresolved_branch_site_examples"][:2]
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
        unresolved = first_function[
            "largest_return_terminated_segments"][0][
                "unresolved_branch_site_examples"]
        self.assertEqual(
            [
                (
                    row["source_pointer_chain"][0]["register"],
                    row["source_pointer_chain"][0]["field_offset"],
                    row["source_pointer_chain"][1]["field_offset"],
                    row["source_pointer_chain"][2]["source_register"],
                )
                for row in unresolved
            ],
            [
                ("ip", 12, 548, "r0"),
                ("r7", 4, 548, "r0"),
            ],
        )
        first_branch = first_function[
            "largest_return_terminated_segments"][0]["branch_site_examples"][0]
        self.assertEqual(first_branch["instruction"], "bl #0x4ec626")
        self.assertEqual(
            (
                first_branch["target_owner"]["component"],
                first_branch["target_owner"]["region"],
                first_branch["target_owner"]["address_status"],
            ),
            (
                "apollo_main",
                "opaque_after_pb_even_ai_before_ring_battery_service",
                "official_blob",
            ),
        )
        self.assertEqual(
            first_function["vector_examples"],
            [
                {
                    "offset": 1458,
                    "mnemonic": "vsri.8",
                    "op_str": "d11, d16, #8",
                    "size": 4,
                },
            ],
        )
        self.assertEqual(
            first_function["pc_reference_examples"][0],
            {
                "offset": 300,
                "instruction": "pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}",
                "target_offset": None,
                "target_relation": "pc_control_operand",
            },
        )

    def test_frontier_coverage_is_complete(self) -> None:
        coverage = self.report["frontier_coverage"]
        self.assertTrue(coverage["all_release_blocking_components_have_frontier"])
        self.assertEqual(coverage["missing_frontier_components"], [])
        self.assertEqual(
            {
                name: row["coverage"]
                for name, row in coverage["components"].items()
            },
            {
                "apollo_bootloader": "retained_official_interval_frontier",
                "apollo_main": "am_boundary_audits_and_raw_transcript_gate",
                "ble_em9305": "residual_readiness_and_largest_span",
                "case": "physical_bucket_and_board_route_frontier",
                "codec": "typed_external_span_map",
                "touch": "physical_bucket_and_resident_abi_frontier",
            },
        )
        self.assertEqual(
            coverage["components"]["apollo_main"]["frontier_fields"],
            [
                "component_priority.source_build_route",
                "apollo_main_priority",
                "apollo_main_priority.focused_source_function_frontier",
                "apollo_retained_hot_target_frontier",
                "primary_global_gate",
            ],
        )
        self.assertIn(
            "typed_physical_bucket_bytes",
            coverage["components"]["touch"]["frontier_fields"],
        )
        self.assertIn(
            "source_only_macos_route",
            coverage["components"]["codec"]["frontier_fields"],
        )
        self.assertIn(
            "source_build_route",
            coverage["components"]["ble_em9305"]["frontier_fields"],
        )
        self.assertIn(
            "source_build_route",
            coverage["components"]["apollo_bootloader"]["frontier_fields"],
        )
        self.assertIn(
            "source_only_macos_route",
            coverage["components"]["case"]["frontier_fields"],
        )
        self.assertIn(
            "source_only_macos_route",
            coverage["components"]["touch"]["frontier_fields"],
        )

    def test_remediation_queue_is_ranked(self) -> None:
        self.assertEqual(
            [
                (row["priority"], row["scope"], row["kind"])
                for row in self.report["remediation_queue"]
            ],
            [
                (0, "source_ownership_quality", "global_gate"),
                (1, "apollo_main", "component_release_blocker"),
                (2, "codec", "component_release_blocker"),
                (3, "ble_em9305", "component_release_blocker"),
                (4, "apollo_bootloader", "component_release_blocker"),
                (5, "case", "component_release_blocker"),
                (6, "touch", "component_release_blocker"),
            ],
        )
        self.assertEqual(
            self.report["remediation_queue"][0]["exit_criteria"],
            self.report["next_pull_through_frontier"]["primary_global_gate"][
                "exit_criteria"],
        )
        self.assertEqual(
            self.report["remediation_queue"][1]["blocking_bytes"],
            3032198,
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
