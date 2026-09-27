import json
import unittest

from tools import analyze_g2_source_ownership_quality_blockers as analyzer
from tools import analyze_g2_untracked_overlay_inputs as untracked_analyzer


class G2SourceOwnershipQualityBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_source_ownership_quality_blockers_are_pinned(self) -> None:
        self.assertFalse(self.report["source_ownership_suitable"])
        self.assertEqual(
            self.report["quality_gate"],
            "fail_closed_raw_instruction_transcription_not_source_owned",
        )
        self.assertEqual(
            self.report["public_unrouted_raw_instruction_source_count"], 102)
        self.assertEqual(
            self.report["public_unrouted_raw_instruction_source_bytes"], 584954)
        self.assertEqual(
            self.report["untracked_overlay_source_input_count"], 0)
        self.assertEqual(
            self.report["gate_blocking_metrics"],
            {
                "source_owned_bytes_currently_overstated": 1830,
                "public_raw_executable_transcript_files": 131,
                "public_unrouted_raw_instruction_transcript_files": 102,
                "public_unrouted_raw_instruction_transcript_bytes": 584954,
                "public_unrouted_raw_instruction_overlay_referenced_files": 102,
                "public_unrouted_raw_instruction_overlay_referenced_bytes": 584954,
                "public_unrouted_raw_instruction_unreferenced_files": 0,
                "public_unrouted_raw_instruction_unreferenced_bytes": 0,
                "untracked_raw_bearing_overlay_source_inputs": 0,
            },
        )
        self.assertEqual(
            self.report["context_metrics"],
            {
                "untracked_overlay_source_inputs": 0,
                "untracked_raw_bearing_overlay_source_inputs": 0,
                "untracked_non_raw_overlay_source_inputs": 0,
                "removed_public_transcript_files": 4,
                "removed_public_transcript_executable_bytes": 21146,
            },
        )

    def test_retired_transcript_boundaries_are_pinned(self) -> None:
        retired = self.report["removed_public_transcript_boundaries"]
        self.assertEqual(len(retired), 4)
        self.assertEqual(
            sum(row["retained_official_executable_bytes"] for row in retired),
            21146,
        )

    def test_largest_raw_sources_are_pinned(self) -> None:
        largest = self.report["largest_public_unrouted_raw_instruction_sources"]
        self.assertEqual(largest[0]["source"],
                         "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c")
        self.assertEqual(largest[0]["inst_directive_bytes"], 10230)
        self.assertTrue(largest[0]["overlay_referenced"])
        self.assertTrue(all(row["overlay_referenced"] for row in largest))
        self.assertEqual(len(largest), 12)

    def test_untracked_overlay_subreport_matches_quality_digest(self) -> None:
        untracked = untracked_analyzer.analyze()
        self.assertEqual(
            self.report["untracked_overlay_source_input_path_sha256"],
            untracked["path_set_sha256"],
        )
        self.assertEqual(
            self.report["untracked_overlay_source_input_count"],
            untracked["input_count"],
        )

    def test_raw_transcript_frontier_is_pinned(self) -> None:
        frontier = self.report["raw_transcript_frontier"]
        expected_raw_ranges = [
            {"first": 23, "last": 23, "count": 1},
            {"first": 69, "last": 69, "count": 1},
            {"first": 81, "last": 87, "count": 7},
            {"first": 89, "last": 95, "count": 7},
            {"first": 97, "last": 141, "count": 45},
            {"first": 143, "last": 183, "count": 41},
        ]
        self.assertEqual(frontier["am_helper_ranges"], expected_raw_ranges)
        self.assertEqual(frontier["raw_bearing_am_helper_ranges"],
                         [])
        self.assertEqual(frontier["non_raw_am_helper_ranges"], [])
        self.assertEqual(frontier["raw_bearing_input_count"], 0)
        self.assertEqual(frontier["non_raw_input_count"], 0)
        self.assertEqual(
            [
                (row["first"], row["last"], row["inst_directive_bytes"])
                for row in frontier["raw_helper_batch_frontier"]
            ],
            [
                (97, 141, 240164),
                (143, 183, 238540),
                (89, 95, 47226),
                (81, 87, 39052),
                (69, 69, 10176),
                (23, 23, 9796),
            ],
        )
        self.assertEqual(
            [
                (row["first"], row["last"], row["inst_directive_bytes"])
                for row in frontier[
                    "top_raw_helper_batch_decomposition"]["subranges"]
            ],
            [
                (116, 134, 113806),
                (97, 115, 91068),
                (135, 141, 35290),
            ],
        )
        focused = frontier["focused_raw_helper_subrange"]
        self.assertEqual(
            (focused["first"], focused["last"], focused["inst_directive_bytes"]),
            (135, 153, 118616),
        )
        self.assertEqual(
            focused["reason_counts"][
                "pc_relative_or_pc_operand_needs_boundary_model"],
            18,
        )
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
                868, 1, 1, 0, 0x005BED12,
                676, 8, 0, 42, 0,
                624, 1, 1, 0, 0x005BC942,
                296, 3, 3, 17,
                282, 2, 14, 0,
                274, 0, 2, 33, 0,
                268, 3, 7, 8,
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
            (147, 23, 9696, 23, 9696, 20, 18, 210, 0, 1596, 0, 4, 1),
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
            (18, [145, 152, 147, 144, 146], 118616, 486, 118616, 418, 0),
        )
        largest = frontier["largest_source_function_frontier"]
        self.assertEqual(
            (
                largest["number"],
                largest["blocked_function_count"],
                largest["blocked_function_bytes"],
                largest["blocked_functions"][0]["function"],
                largest["blocked_functions"][0]["byte_length"],
            ),
            (
                115,
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
                        "semantic_frontier"]["implementation_readiness"],
                [
                    row["semantic_frontier"]["kind"]
                    for row in largest["largest_function_shape"][
                        "ranked_entry_pull_through_queue"][1:10]
                ],
                largest["largest_function_shape"][
                    "ranked_entry_semantic_rollup"]["classified_rank_count"],
                largest["largest_function_shape"][
                    "ranked_entry_semantic_rollup"]["decode_only_ranks"],
            ),
            (1750, 10, 11, 1632, 11, False, 10, 1238, 32, 12,
             "pop {r1, pc}", "gated_literal_call_returns_zero",
             "not_yet_routed_into_overlay", 0x200746A8, 0x0078E144,
             0x200031B4, [1238, 254, 880, 1050], [12, 61, 65, 72],
             "gated_stack_path_builder_returns_zero",
             "needs_path_helper_semantics", [
                 "gated_stack_path_builder_returns_zero",
                 "gated_stack_path_builder_status_log_returns_zero",
                 "gated_stack_path_builder_extended_output_returns_zero",
                 "gated_dynamic_path_query_extended_output_returns_zero",
                 "gated_path_component_filter_join_returns_status",
                 "gated_dynamic_path_normalize_query_persist_returns_zero",
                 "storage_context_metrics_log_returns_zero",
                 "gated_dynamic_path_normalize_iterative_query_dump_returns_zero",
                 "gated_two_token_path_compare_update_returns_zero",
             ], 10, []),
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
                    "bytes_through_return"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["kind"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["call_target"],
                next_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                next_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
            ),
            (
                1932,
                13,
                12,
                0x00545EC4,
                10,
                "u16_argument_tail_call_wrapper",
                0x00486876,
                12,
                0,
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
                    "decode_only_ranks"],
                [
                    row["semantic_frontier"]["kind"]
                    for row in third_shape["ranked_entry_pull_through_queue"]
                ],
            ),
            (
                952,
                2,
                2,
                [],
                [
                    "u8_status_query_with_debug_logs",
                    "retry_transaction_fill_compact_result",
                ],
            ),
        )
        fourth_shape = largest["fourth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_byte_count"],
                fourth_shape["entry_candidate_count"],
                fourth_shape["function_semantic_frontier"]["kind"],
                fourth_shape["function_semantic_frontier"]["transaction_call"],
                fourth_shape["function_semantic_frontier"][
                    "firmware_routing_status"],
            ),
            (
                520,
                0,
                "prologueless_retry_transaction_tail_fill_u16_result",
                0x00544532,
                "not_yet_routed_into_overlay",
            ),
        )
        fifth_shape = largest["fifth_blocked_function_shape"]
        self.assertEqual(
            (
                fifth_shape["directive_byte_count"],
                fifth_shape["entry_candidate_count"],
                fifth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                fifth_shape["ranked_entry_semantic_rollup"][
                    "decode_only_ranks"],
                fifth_shape["ranked_entry_pull_through_queue"][3][
                    "semantic_frontier"]["kind"],
            ),
            (
                438,
                5,
                4,
                [],
                "device_state_format_buffer_returns_pointer",
            ),
        )
        sixth_shape = largest["sixth_blocked_function_shape"]
        self.assertEqual(
            (
                sixth_shape["directive_byte_count"],
                sixth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
                sixth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["kind"],
                sixth_shape["ranked_entry_pull_through_queue"][1][
                    "semantic_frontier"]["action_call"],
            ),
            (
                336,
                2,
                "dynamic_segment_command_dispatch_returns_zero",
                0x005576BA,
            ),
        )
        seventh_shape = largest["seventh_blocked_function_shape"]
        self.assertEqual(
            (
                seventh_shape["directive_byte_count"],
                seventh_shape["bounded_local_return_entry_count"],
                seventh_shape["entry_candidates"][0]["entry_address"],
                seventh_shape["function_semantic_frontier"]["kind"],
                seventh_shape["function_semantic_frontier"][
                    "embedded_query_call"],
            ),
            (
                334,
                0,
                0x005457B4,
                "split_status_query_debug_tail_and_embedded_probe",
                0x00544E98,
            ),
        )
        eighth_shape = largest["eighth_blocked_function_shape"]
        self.assertEqual(
            (
                eighth_shape["directive_byte_count"],
                eighth_shape["bounded_local_return_entry_count"],
                eighth_shape["unbounded_or_overlapping_entry_count"],
                eighth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["query_call"],
                eighth_shape["function_semantic_frontier"][
                    "second_embedded_entry_address"],
            ),
            (
                302,
                1,
                1,
                0x00544850,
                0x00545504,
            ),
        )
        ninth_shape = largest["ninth_blocked_function_shape"]
        self.assertEqual(
            (
                ninth_shape["directive_byte_count"],
                ninth_shape["entry_candidate_count"],
                ninth_shape["function_semantic_frontier"]["kind"],
                ninth_shape["function_semantic_frontier"]["read_call"],
            ),
            (
                222,
                0,
                "prologueless_retry_read_status_tail_with_cleanup",
                0x00543D26,
            ),
        )
        tenth_shape = largest["tenth_blocked_function_shape"]
        self.assertEqual(
            (
                tenth_shape["directive_byte_count"],
                tenth_shape["entry_candidate_count"],
                tenth_shape["function_semantic_frontier"]["kind"],
                tenth_shape["function_semantic_frontier"][
                    "status_output_register"],
            ),
            (
                206,
                0,
                "prologueless_u16_status_pack_tail_with_cleanup",
                "r5",
            ),
        )
        eleventh_shape = largest["eleventh_blocked_function_shape"]
        self.assertEqual(
            (
                eleventh_shape["directive_byte_count"],
                eleventh_shape["first_return_halfword_index"],
                eleventh_shape["function_semantic_frontier"]["kind"],
                eleventh_shape["function_semantic_frontier"][
                    "transaction_call"],
            ),
            (
                200,
                96,
                "prologueless_retry_transaction_tail_fill_u8_result",
                0x00544532,
            ),
        )
        twelfth_shape = largest["twelfth_blocked_function_shape"]
        self.assertEqual(
            (
                twelfth_shape["directive_byte_count"],
                twelfth_shape["entry_candidate_count"],
                twelfth_shape["function_semantic_frontier"]["kind"],
                twelfth_shape["function_semantic_frontier"][
                    "filter_join_call_count"],
            ),
            (
                188,
                0,
                "prologueless_dual_path_filter_join_tail",
                2,
            ),
        )
        thirteenth_shape = largest["thirteenth_blocked_function_shape"]
        self.assertEqual(
            (
                len(largest["blocked_functions"]),
                thirteenth_shape["directive_byte_count"],
                thirteenth_shape["entry_candidate_count"],
                thirteenth_shape["function_semantic_frontier"]["kind"],
                thirteenth_shape["function_semantic_frontier"][
                    "success_tail_entry"],
            ),
            (
                27,
                182,
                0,
                "prologueless_transaction_setup_tail_to_retry_read_status",
                0x00545320,
            ),
        )
        fourteenth_shape = largest["fourteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fourteenth_shape["directive_byte_count"],
                fourteenth_shape["entry_candidate_count"],
                fourteenth_shape["function_semantic_frontier"]["kind"],
                fourteenth_shape["function_semantic_frontier"][
                    "continuation_tail_entry"],
            ),
            (
                162,
                0,
                "prologueless_dual_path_input_staging_tail",
                0x005477AC,
            ),
        )
        fifteenth_shape = largest["fifteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fifteenth_shape["directive_byte_count"],
                fifteenth_shape["entry_candidate_count"],
                fifteenth_shape["entry_candidates"][0]["entry_address"],
                fifteenth_shape["function_semantic_frontier"]["kind"],
            ),
            (
                106,
                1,
                0x00544D0C,
                "literal_prefix_embedded_retry_search_entry",
            ),
        )
        sixteenth_shape = largest["sixteenth_blocked_function_shape"]
        self.assertEqual(
            (
                sixteenth_shape["directive_byte_count"],
                sixteenth_shape["return_like_count"],
                sixteenth_shape["function_semantic_frontier"]["kind"],
                sixteenth_shape["function_semantic_frontier"][
                    "embedded_following_entry_address"],
            ),
            (
                106,
                1,
                "prologueless_u8_status_debug_return_tail",
                0x005456D4,
            ),
        )
        seventeenth_shape = largest["seventeenth_blocked_function_shape"]
        self.assertEqual(
            (
                seventeenth_shape["directive_byte_count"],
                seventeenth_shape["entry_candidate_count"],
                seventeenth_shape["function_semantic_frontier"]["kind"],
                seventeenth_shape["function_semantic_frontier"][
                    "embedded_entry_address"],
            ),
            (
                100,
                1,
                "literal_prefix_embedded_retry_option_initializer",
                0x00545044,
            ),
        )
        eighteenth_shape = largest["eighteenth_blocked_function_shape"]
        self.assertEqual(
            (
                eighteenth_shape["directive_byte_count"],
                eighteenth_shape["entry_candidate_count"],
                eighteenth_shape["function_semantic_frontier"]["kind"],
                eighteenth_shape["function_semantic_frontier"][
                    "retry_search_call"],
            ),
            (
                96,
                0,
                "prologueless_u16_status_query_via_retry_search_tail",
                0x00544D0C,
            ),
        )
        nineteenth_shape = largest["nineteenth_blocked_function_shape"]
        self.assertEqual(
            (
                nineteenth_shape["directive_byte_count"],
                nineteenth_shape["bounded_local_return_entry_count"],
                nineteenth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"]["kind"],
                nineteenth_shape["function_semantic_frontier"][
                    "embedded_compare_entry_address"],
            ),
            (
                80,
                1,
                "vfp_d0_d1_compare_wrapper",
                0x00545C74,
            ),
        )
        twentieth_shape = largest["twentieth_blocked_function_shape"]
        self.assertEqual(
            (
                twentieth_shape["directive_byte_count"],
                twentieth_shape["bounded_local_return_entry_count"],
                twentieth_shape["function_semantic_frontier"]["kind"],
                twentieth_shape["function_semantic_frontier"][
                    "embedded_status_entry_address"],
                twentieth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                58,
                0,
                "split_debug_tail_literal_pool_and_embedded_status_setup",
                0x00545890,
                "needs_boundary_reconciliation_before_crc_or_status_semantics",
            ),
        )
        twenty_first_shape = largest["twenty_first_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_first_shape["directive_byte_count"],
                twenty_first_shape["entry_candidate_count"],
                twenty_first_shape["function_semantic_frontier"]["kind"],
                twenty_first_shape["function_semantic_frontier"][
                    "log_format_call"],
                twenty_first_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                50,
                0,
                "prologueless_four_stage_debug_log_dispatch_tail",
                0x00405594,
                "needs_four_stage_debug_log_tail_semantics",
            ),
        )
        twenty_second_shape = largest["twenty_second_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_second_shape["directive_byte_count"],
                twenty_second_shape["entry_candidate_count"],
                twenty_second_shape["function_semantic_frontier"]["kind"],
                twenty_second_shape["function_semantic_frontier"][
                    "shared_return_tail_entry"],
                twenty_second_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                40,
                0,
                "prologueless_compass_debug_tail_to_shared_return",
                0x0054566A,
                "needs_compass_debug_tail_boundary_semantics",
            ),
        )
        twenty_third_shape = largest["twenty_third_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_third_shape["directive_byte_count"],
                twenty_third_shape["entry_candidate_count"],
                twenty_third_shape["function_semantic_frontier"]["kind"],
                twenty_third_shape["function_semantic_frontier"][
                    "debug_emit_code"],
                twenty_third_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                36,
                0,
                "prologueless_condition_flag_debug_emit_tail",
                0x10800000,
                "needs_condition_flag_debug_emit_tail_semantics",
            ),
        )
        twenty_fourth_shape = largest["twenty_fourth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fourth_shape["directive_byte_count"],
                twenty_fourth_shape["entry_candidate_count"],
                twenty_fourth_shape["function_semantic_frontier"]["kind"],
                twenty_fourth_shape["function_semantic_frontier"]["query_call"],
                twenty_fourth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                32,
                0,
                "prologueless_status_query_setup_tail_with_decompile_conflict",
                0x00544E98,
                "needs_status_query_tail_boundary_reconciliation",
            ),
        )
        twenty_fifth_shape = largest["twenty_fifth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fifth_shape["directive_byte_count"],
                twenty_fifth_shape["unbounded_or_overlapping_entry_count"],
                twenty_fifth_shape["function_semantic_frontier"]["kind"],
                twenty_fifth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                30,
                1,
                "split_return_literal_pool_and_embedded_two_call_entry",
                "needs_two_call_entry_boundary_reconciliation",
            ),
        )
        twenty_sixth_shape = largest["twenty_sixth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_sixth_shape["directive_byte_count"],
                twenty_sixth_shape["entry_candidate_count"],
                twenty_sixth_shape["function_semantic_frontier"]["kind"],
                twenty_sixth_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                12,
                0,
                "prologueless_opacity_debug_literal_prefix",
                "needs_opacity_debug_prefix_boundary_reconciliation",
            ),
        )
        twenty_seventh_shape = largest["twenty_seventh_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_seventh_shape["directive_byte_count"],
                twenty_seventh_shape["entry_candidate_count"],
                twenty_seventh_shape["function_semantic_frontier"]["kind"],
                twenty_seventh_shape["function_semantic_frontier"][
                    "implementation_readiness"],
            ),
            (
                10,
                0,
                "prologueless_retry_service_tail_branch_fragment",
                "needs_retry_service_tail_branch_semantics",
            ),
        )
        self.assertEqual(
            frontier["mixed_boundary_reason_counts"],
            {
                "it_block_requires_conditional_text_or_whole_body_source": 38,
                "linear_raw_instruction_text_still_needs_source_model": 89,
                "nonlinear_data_or_literal_island": 102,
                "pc_relative_or_pc_operand_needs_boundary_model": 98,
                "vector_instruction_text_not_apple_clang_roundtrip_safe": 67,
            },
        )

    def test_retained_hot_target_recovery_contracts_are_pinned(self) -> None:
        frontier = self.report["retained_hot_target_recovery_frontier"]
        self.assertTrue(frontier["available"])
        self.assertEqual(
            frontier["manifest"],
            "tools/manifests/g2-apollo-retained-hot-targets.json",
        )
        rollup = frontier["rollup"]
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
            {
                key: rollup["am142_target_compile_receipt"][key]
                for key in (
                    "available",
                    "manifest",
                    "object_sha256",
                    "undefined_symbol_count",
                    "relocation_count",
                    "symbol_count",
                    "target_compile_verified",
                    "toolchain_profile",
                    "firmware_routing_status",
                )
            },
            {
                "available": True,
                "manifest": (
                    "tools/manifests/"
                    "g2-apollo-am142-pullthrough-candidate.json"
                ),
                "object_sha256": (
                    "273ca76794e7ba222098acaaa9913a6d5e5effb741f95c23bc755c3eecfcf43c"
                ),
                "undefined_symbol_count": 0,
                "relocation_count": 28,
                "symbol_count": 28,
                "target_compile_verified": True,
                "toolchain_profile": "apple-clang",
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
                    "bl #0x43f09a",
                    "call_shim_to_retained_helper",
                ),
            ],
        )
        contracts = frontier["contracts"]
        first = contracts[0]
        self.assertEqual(len(contracts), 6)
        self.assertEqual(
            (
                first["priority"],
                first["region"],
                first["dependency_class"],
                first["start_address"],
                first["end_address"],
                first["byte_length"],
                first["instruction_count"],
            ),
            (
                1,
                "opaque_between_ring_buffer_and_pb_translate_split_0016025c_00165264",
                "isolated_window",
                0x0059A312,
                0x0059A3A6,
                148,
                44,
            ),
        )
        self.assertEqual(
            (
                first["source_recovery_status"]["status"],
                first["source_recovery_status"]["current_representation"],
                first["source_recovery_status"]["terminal_branch"][
                    "instruction"],
                first["source_recovery_status"]["terminal_branch"][
                    "target_address"],
            ),
            (
                "requires_c_pull_through",
                "retained_exact_helper_bytes",
                "bge #0x59a45c",
                0x0059A45C,
            ),
        )
        self.assertEqual(
            (
                first["source_recovery_status"]["translation_summary"][
                    "shape"],
                first["source_recovery_status"]["translation_summary"][
                    "instruction_count"],
                first["source_recovery_status"]["translation_summary"][
                    "memory_instruction_count"],
                first["source_recovery_status"]["translation_summary"][
                    "vfp_instruction_count"],
                first["source_recovery_status"]["translation_summary"][
                    "mnemonic_counts"]["vmls.f32"],
            ),
            (
                "straight_line_to_terminal_branch",
                44,
                9,
                26,
                4,
            ),
        )
        self.assertEqual(
            first["arithmetic_motif"]["kind"],
            "squared_delta_accumulator",
        )
        self.assertEqual(
            (
                first["arithmetic_motif"]["source_model"][
                    "c_translation_status"],
                first["arithmetic_motif"]["source_model"]["operations"][-1],
                first["arithmetic_motif"]["source_model"]["abi_contract"][
                    "branch_condition"],
                first["arithmetic_motif"]["source_model"]["abi_validation"][
                    "matches_decoded_features"],
                first["arithmetic_motif"]["source_model"]["abi_validation"][
                    "observed_s16_write_count"],
                first["arithmetic_motif"]["source_model"][
                    "reference_evidence"]["firmware_routing_status"],
                first["arithmetic_motif"]["source_model"][
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

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
