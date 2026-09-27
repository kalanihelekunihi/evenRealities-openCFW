import json
import unittest

from tools import analyze_g2_gate_raw_transcript_blockers as analyzer


class G2GateRawTranscriptBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_gate_raw_transcript_blockers_are_pinned(self) -> None:
        self.assertFalse(self.report["source_ownership_suitable"])
        self.assertEqual(self.report["raw_transcript_source_count"], 102)
        self.assertEqual(self.report["raw_transcript_bytes"], 584954)
        self.assertEqual(
            self.report["mixed_boundary_reason_counts"],
            {
                "it_block_requires_conditional_text_or_whole_body_source": 38,
                "linear_raw_instruction_text_still_needs_source_model": 89,
                "nonlinear_data_or_literal_island": 102,
                "pc_relative_or_pc_operand_needs_boundary_model": 98,
                "vector_instruction_text_not_apple_clang_roundtrip_safe": 67,
            },
        )
        self.assertEqual(
            self.report["mixed_boundary_function_class_counts"][
                "linear:linear_raw_instruction_text_still_needs_source_model"],
            {"functions": 693, "bytes": 69030},
        )
        self.assertEqual(
            self.report["mixed_boundary_function_class_counts"][
                "mixed:nonlinear_data_or_literal_island"],
            {"functions": 742, "bytes": 117534},
        )
        self.assertEqual(
            self.report["am_helper_ranges"],
            [
                {"first": 23, "last": 23, "count": 1},
                {"first": 69, "last": 69, "count": 1},
                {"first": 81, "last": 87, "count": 7},
                {"first": 89, "last": 95, "count": 7},
                {"first": 97, "last": 141, "count": 45},
                {"first": 143, "last": 183, "count": 41},
            ],
        )

    def test_largest_sources_are_pinned(self) -> None:
        largest = self.report["largest_sources"]
        self.assertEqual(largest[0]["source"],
                         "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c")
        self.assertEqual(largest[0]["inst_directive_bytes"], 10230)
        self.assertEqual(len(largest), 12)

    def test_raw_helper_batch_frontier_is_ranked(self) -> None:
        self.assertEqual(
            [
                (row["first"], row["last"], row["count"],
                 row["inst_directive_bytes"],
                 row["largest_source"]["source"])
                for row in self.report["raw_helper_batch_frontier"]
            ],
            [
                (
                    97,
                    141,
                    45,
                    240164,
                    "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c",
                ),
                (
                    143,
                    183,
                    41,
                    238540,
                    "components/apollo_main/core_overlay/runtime_liblc3_am167_helpers.c",
                ),
                (
                    89,
                    95,
                    7,
                    47226,
                    "components/apollo_main/core_overlay/runtime_liblc3_am092_helpers.c",
                ),
                (
                    81,
                    87,
                    7,
                    39052,
                    "components/apollo_main/core_overlay/runtime_liblc3_am085_helpers.c",
                ),
                (
                    69,
                    69,
                    1,
                    10176,
                    "components/apollo_main/core_overlay/runtime_liblc3_am069_helpers.c",
                ),
                (
                    23,
                    23,
                    1,
                    9796,
                    "components/apollo_main/core_overlay/runtime_liblc3_am023_helpers.c",
                ),
            ],
        )

    def test_top_raw_helper_batch_decomposition_is_pinned(self) -> None:
        top = self.report["top_raw_helper_batch_decomposition"]
        self.assertEqual(
            (top["first"], top["last"], top["count"], top["inst_directive_bytes"]),
            (97, 141, 45, 240164),
        )
        self.assertEqual(
            [
                (row["number"], row["inst_directive_bytes"])
                for row in top["top_sources"][:5]
            ],
            [
                (115, 10230),
                (127, 10126),
                (117, 10104),
                (118, 10060),
                (97, 9896),
            ],
        )
        self.assertEqual(
            [
                (row["first"], row["last"], row["count"],
                 row["inst_directive_bytes"],
                 row["largest_source"]["number"])
                for row in top["subranges"]
            ],
            [
                (116, 134, 19, 113806, 127),
                (97, 115, 19, 91068, 115),
                (135, 141, 7, 35290, 141),
            ],
        )

    def test_focused_raw_helper_subrange_is_pinned(self) -> None:
        focused = self.report["focused_raw_helper_subrange"]
        self.assertEqual(
            (focused["first"], focused["last"], focused["count"],
             focused["inst_directive_bytes"]),
            (135, 153, 18, 118616),
        )
        self.assertEqual(
            focused["reason_counts"],
            {
                "it_block_requires_conditional_text_or_whole_body_source": 4,
                "linear_raw_instruction_text_still_needs_source_model": 18,
                "nonlinear_data_or_literal_island": 18,
                "pc_relative_or_pc_operand_needs_boundary_model": 18,
                "vector_instruction_text_not_apple_clang_roundtrip_safe": 6,
            },
        )
        self.assertEqual(
            [
                (row["number"], row["inst_directive_bytes"],
                 row["blocked_function_count"], row["blocked_function_bytes"])
                for row in focused["top_sources"][:6]
            ],
            [
                (145, 9850, 32, 9850),
                (152, 9828, 28, 9828),
                (147, 9696, 23, 9696),
                (144, 9536, 29, 9536),
                (146, 9338, 32, 9338),
                (151, 8586, 32, 8586),
            ],
        )
        frontier = focused["top_source_function_frontier"]
        self.assertEqual(
            (
                frontier["number"],
                frontier["source"],
                frontier["inst_directive_bytes"],
                frontier["blocked_function_count"],
                frontier["blocked_function_bytes"],
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
            [
                (row["function"], row["byte_length"])
                for row in frontier["blocked_functions"][:5]
            ],
            [
                ("open_cfw_runtime_am145_0x005a490c", 1012),
                ("open_cfw_runtime_am145_0x005a45d0", 782),
                ("open_cfw_runtime_am145_0x005a6d10", 674),
                ("open_cfw_runtime_am145_0x005a65de", 632),
                ("open_cfw_runtime_am145_0x005a326c", 606),
            ],
        )
        shape = frontier["largest_blocked_function_shape"]
        self.assertEqual(
            (
                shape["directive_halfword_count"],
                shape["directive_byte_count"],
                shape["push_like_prologue_count"],
                shape["return_like_count"],
                shape["entry_candidate_count"],
                shape["bounded_local_return_entry_count"],
                shape["unbounded_or_overlapping_entry_count"],
                shape["ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (506, 1012, 1, 4, 1, 1, 0, 0),
        )
        self.assertEqual(
            (
                shape["ranked_entry_pull_through_queue"][0]["entry_address"],
                shape["ranked_entry_pull_through_queue"][0][
                    "bytes_through_return"],
            ),
            (0x005A4A66, 208),
        )
        next_shape = frontier["next_blocked_function_shape"]
        self.assertEqual(
            (
                next_shape["directive_byte_count"],
                next_shape["push_like_prologue_count"],
                next_shape["return_like_count"],
                next_shape["entry_candidate_count"],
                next_shape["bounded_local_return_entry_count"],
                next_shape["unbounded_or_overlapping_entry_count"],
                next_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (782, 1, 6, 1, 1, 0, 0),
        )
        self.assertEqual(
            (
                next_shape["ranked_entry_pull_through_queue"][0][
                    "entry_address"],
                next_shape["ranked_entry_pull_through_queue"][0][
                    "bytes_through_return"],
                next_shape["entry_candidates"][0]["post_return_tail_bytes"],
            ),
            (0x005A4802, 120, 100),
        )
        self.assertEqual(
            next_shape["ranked_entry_pull_through_queue"][0][
                "semantic_frontier"]["implementation_readiness"],
            "needs_am145_tail_wrapper_semantics",
        )
        third_shape = frontier["third_blocked_function_shape"]
        self.assertEqual(
            (
                third_shape["directive_byte_count"],
                third_shape["push_like_prologue_count"],
                third_shape["return_like_count"],
                third_shape["entry_candidate_count"],
                third_shape["bounded_local_return_entry_count"],
                third_shape["unbounded_or_overlapping_entry_count"],
                third_shape["ranked_entry_semantic_rollup"]["decode_only_count"],
            ),
            (674, 1, 1, 1, 1, 0, 0),
        )
        self.assertEqual(
            (
                third_shape["ranked_entry_pull_through_queue"][0][
                    "entry_address"],
                third_shape["ranked_entry_pull_through_queue"][0][
                    "bytes_through_return"],
            ),
            (0x005A6E34, 22),
        )
        self.assertEqual(
            third_shape["ranked_entry_pull_through_queue"][0][
                "semantic_frontier"]["implementation_readiness"],
            "needs_am145_conditional_tail_semantics",
        )
        fourth_shape = frontier["fourth_blocked_function_shape"]
        fifth_shape = frontier["fifth_blocked_function_shape"]
        sixth_shape = frontier["sixth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_byte_count"],
                fourth_shape["push_like_prologue_count"],
                fourth_shape["return_like_count"],
                fourth_shape["entry_candidate_count"],
                fourth_shape["branch_like_halfword_count"],
                fifth_shape["directive_byte_count"],
                fifth_shape["push_like_prologue_count"],
                fifth_shape["return_like_count"],
                fifth_shape["entry_candidate_count"],
                fifth_shape["branch_like_halfword_count"],
                sixth_shape["directive_byte_count"],
                sixth_shape["push_like_prologue_count"],
                sixth_shape["return_like_count"],
                sixth_shape["entry_candidate_count"],
                sixth_shape["branch_like_halfword_count"],
            ),
            (632, 3, 6, 3, 38, 606, 1, 0, 1, 29, 552, 5, 5, 5, 26),
        )
        seventh_shape = frontier["seventh_blocked_function_shape"]
        eighth_shape = frontier["eighth_blocked_function_shape"]
        ninth_shape = frontier["ninth_blocked_function_shape"]
        tenth_shape = frontier["tenth_blocked_function_shape"]
        self.assertEqual(
            (
                seventh_shape["directive_byte_count"],
                seventh_shape["entry_candidate_count"],
                seventh_shape["bounded_local_return_entry_count"],
                seventh_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                seventh_shape["branch_like_halfword_count"],
                len(seventh_shape["ranked_entry_pull_through_queue"]),
                eighth_shape["directive_byte_count"],
                eighth_shape["entry_candidate_count"],
                eighth_shape["bounded_local_return_entry_count"],
                eighth_shape["ranked_entry_semantic_rollup"][
                    "decode_only_count"],
                eighth_shape["branch_like_halfword_count"],
                len(eighth_shape["ranked_entry_pull_through_queue"]),
                ninth_shape["directive_byte_count"],
                ninth_shape["entry_candidate_count"],
                ninth_shape["branch_like_halfword_count"],
                tenth_shape["directive_byte_count"],
                tenth_shape["entry_candidate_count"],
                tenth_shape["branch_like_halfword_count"],
            ),
            (534, 0, 0, 0, 18, 0, 464, 0, 0, 0, 28, 0, 390, 0, 23, 344, 0, 21),
        )
        eleventh_shape = frontier["eleventh_blocked_function_shape"]
        twelfth_shape = frontier["twelfth_blocked_function_shape"]
        thirteenth_shape = frontier["thirteenth_blocked_function_shape"]
        fourteenth_shape = frontier["fourteenth_blocked_function_shape"]
        fifteenth_shape = frontier["fifteenth_blocked_function_shape"]
        self.assertEqual(
            (
                eleventh_shape["directive_byte_count"],
                eleventh_shape["entry_candidate_count"],
                eleventh_shape["unbounded_or_overlapping_entry_count"],
                eleventh_shape["branch_like_halfword_count"],
                len(eleventh_shape["ranked_entry_pull_through_queue"]),
                twelfth_shape["directive_byte_count"],
                twelfth_shape["entry_candidate_count"],
                twelfth_shape["bounded_local_return_entry_count"],
                twelfth_shape["branch_like_halfword_count"],
                len(twelfth_shape["ranked_entry_pull_through_queue"]),
                thirteenth_shape["directive_byte_count"],
                thirteenth_shape["entry_candidate_count"],
                thirteenth_shape["branch_like_halfword_count"],
                fourteenth_shape["directive_byte_count"],
                fourteenth_shape["entry_candidate_count"],
                fourteenth_shape["branch_like_halfword_count"],
                fifteenth_shape["directive_byte_count"],
                fifteenth_shape["entry_candidate_count"],
                fifteenth_shape["branch_like_halfword_count"],
            ),
            (
                310, 0, 0, 18, 0,
                302, 0, 0, 12, 0,
                294, 0, 10,
                284, 0, 16,
                272, 1, 6,
            ),
        )
        sixteenth_shape = frontier["sixteenth_blocked_function_shape"]
        seventeenth_shape = frontier["seventeenth_blocked_function_shape"]
        eighteenth_shape = frontier["eighteenth_blocked_function_shape"]
        nineteenth_shape = frontier["nineteenth_blocked_function_shape"]
        twentieth_shape = frontier["twentieth_blocked_function_shape"]
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
                nineteenth_shape["branch_like_halfword_count"],
                twentieth_shape["directive_byte_count"],
                twentieth_shape["entry_candidate_count"],
                twentieth_shape["branch_like_halfword_count"],
            ),
            (
                256, 0, 18,
                250, 0, 9,
                232, 2, 6,
                212, 0, 0, 14,
                210, 0, 15,
            ),
        )
        twenty_first_shape = frontier["twenty_first_blocked_function_shape"]
        twenty_second_shape = frontier["twenty_second_blocked_function_shape"]
        twenty_third_shape = frontier["twenty_third_blocked_function_shape"]
        twenty_fourth_shape = frontier["twenty_fourth_blocked_function_shape"]
        twenty_fifth_shape = frontier["twenty_fifth_blocked_function_shape"]
        twenty_sixth_shape = frontier["twenty_sixth_blocked_function_shape"]
        twenty_seventh_shape = frontier["twenty_seventh_blocked_function_shape"]
        twenty_eighth_shape = frontier["twenty_eighth_blocked_function_shape"]
        twenty_ninth_shape = frontier["twenty_ninth_blocked_function_shape"]
        thirtieth_shape = frontier["thirtieth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_first_shape["directive_byte_count"],
                twenty_first_shape["entry_candidate_count"],
                twenty_first_shape["branch_like_halfword_count"],
                twenty_second_shape["directive_byte_count"],
                twenty_second_shape["entry_candidate_count"],
                twenty_second_shape["branch_like_halfword_count"],
                twenty_third_shape["directive_byte_count"],
                twenty_third_shape["entry_candidate_count"],
                twenty_third_shape["bounded_local_return_entry_count"],
                twenty_third_shape["unbounded_or_overlapping_entry_count"],
                twenty_fourth_shape["directive_byte_count"],
                twenty_fourth_shape["entry_candidate_count"],
                twenty_fourth_shape["unbounded_or_overlapping_entry_count"],
                twenty_fifth_shape["directive_byte_count"],
                twenty_fifth_shape["entry_candidate_count"],
                twenty_fifth_shape["branch_like_halfword_count"],
                twenty_sixth_shape["directive_byte_count"],
                twenty_sixth_shape["entry_candidate_count"],
                twenty_sixth_shape["branch_like_halfword_count"],
                twenty_seventh_shape["directive_byte_count"],
                twenty_seventh_shape["entry_candidate_count"],
                twenty_seventh_shape["branch_like_halfword_count"],
                twenty_eighth_shape["directive_byte_count"],
                twenty_eighth_shape["entry_candidate_count"],
                twenty_eighth_shape["branch_like_halfword_count"],
                twenty_ninth_shape["directive_byte_count"],
                twenty_ninth_shape["entry_candidate_count"],
                twenty_ninth_shape["branch_like_halfword_count"],
                thirtieth_shape["directive_byte_count"],
                thirtieth_shape["entry_candidate_count"],
                thirtieth_shape["return_like_count"],
            ),
            (
                200, 0, 11,
                192, 0, 19,
                138, 1, 0, 1,
                136, 0, 0,
                130, 0, 9,
                104, 0, 3,
                82, 0, 6,
                80, 0, 3,
                66, 2, 2,
                46, 0, 0,
            ),
        )
        next_frontier = focused["next_source_function_frontier"]
        self.assertEqual(
            (
                next_frontier["number"],
                next_frontier["source"],
                next_frontier["blocked_function_count"],
                next_frontier["blocked_function_bytes"],
            ),
            (
                152,
                "components/apollo_main/core_overlay/runtime_liblc3_am152_helpers.c",
                28,
                9828,
            ),
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
        self.assertEqual(
            (
                next_frontier["largest_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["largest_blocked_function_shape"][
                    "ranked_entry_pull_through_queue"][0]["entry_address"],
                next_frontier["next_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["next_blocked_function_shape"][
                    "ranked_entry_pull_through_queue"][0]["entry_address"],
                next_frontier["third_blocked_function_shape"][
                    "directive_byte_count"],
                next_frontier["third_blocked_function_shape"][
                    "ranked_entry_pull_through_queue"][0]["entry_address"],
            ),
            (2426, 0x005BE3C2, 1406, 0x005BDA08, 920, 0x005BD44E),
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
                third_frontier["source"],
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
            (
                147,
                "components/apollo_main/core_overlay/runtime_liblc3_am147_helpers.c",
                23,
                9696,
                23,
                9696,
                20,
                18,
                210,
                0,
                1596,
                0,
                4,
                1,
            ),
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
        largest = self.report["largest_source_function_frontier"]
        self.assertEqual(
            (
                largest["number"],
                largest["source"],
                largest["inst_directive_bytes"],
                largest["blocked_function_count"],
                largest["blocked_function_bytes"],
            ),
            (
                115,
                "components/apollo_main/core_overlay/runtime_liblc3_am115_helpers.c",
                10230,
                27,
                10230,
            ),
        )
        self.assertEqual(
            [
                (row["function"], row["byte_length"], row["reasons"])
                for row in largest["blocked_functions"][:3]
            ],
            [
                (
                    "open_cfw_runtime_am115_0x0054692c",
                    3500,
                    ["nonlinear_data_or_literal_island"],
                ),
                (
                    "open_cfw_runtime_am115_0x00545d18",
                    1932,
                    [
                        "it_block_requires_conditional_text_or_whole_body_source",
                        "pc_relative_or_pc_operand_needs_boundary_model",
                    ],
                ),
                (
                    "open_cfw_runtime_am115_0x005458a2",
                    952,
                    [
                        "nonlinear_data_or_literal_island",
                        "pc_relative_or_pc_operand_needs_boundary_model",
                    ],
                ),
            ],
        )
        self.assertEqual(len(largest["blocked_functions"]), 27)
        self.assertEqual(
            (
                largest["blocked_functions"][12]["function"],
                largest["blocked_functions"][12]["byte_length"],
                largest["blocked_functions"][12]["reasons"],
                largest["blocked_functions"][13]["function"],
                largest["blocked_functions"][13]["byte_length"],
                largest["blocked_functions"][13]["reasons"],
                largest["blocked_functions"][14]["function"],
                largest["blocked_functions"][14]["byte_length"],
                largest["blocked_functions"][14]["reasons"],
                largest["blocked_functions"][15]["function"],
                largest["blocked_functions"][15]["byte_length"],
                largest["blocked_functions"][15]["reasons"],
            ),
            (
                "open_cfw_runtime_am115_0x00545264",
                182,
                ["linear_raw_instruction_text_still_needs_source_model"],
                "open_cfw_runtime_am115_0x005476e4",
                162,
                ["nonlinear_data_or_literal_island"],
                "open_cfw_runtime_am115_0x00544cf6",
                106,
                ["nonlinear_data_or_literal_island"],
                "open_cfw_runtime_am115_0x0054566c",
                106,
                ["pc_relative_or_pc_operand_needs_boundary_model"],
            ),
        )
        shape = largest["largest_function_shape"]
        self.assertEqual(
            (
                shape["directive_halfword_count"],
                shape["directive_byte_count"],
                shape["first_prologue_halfword_index"],
                shape["prefix_before_first_prologue_halfwords"],
                shape["push_like_prologue_count"],
                shape["return_like_count"],
                shape["first_return_halfword_index"],
                shape["branch_like_halfword_count"],
                shape["zero_halfword_count"],
                shape["post_first_return_halfword_count"],
                shape["entry_candidate_count"],
                shape["bounded_local_return_entry_count"],
                shape["unbounded_or_overlapping_entry_count"],
            ),
            (1750, 3500, 10, 10, 11, 11, 117, 188, 13, 1632, 11, 10, 1),
        )
        self.assertEqual(
            shape["first_halfwords"],
            [
                "0xf9f5",
                "0x2000",
                "0xe7ca",
                "0xa29f",
                "0xa902",
                "0xf8df",
                "0x0c14",
                "0xf6f4",
                "0xfd68",
                "0xe7d0",
                "0xb5f8",
                "0xb0c6",
            ],
        )
        self.assertEqual(
            [row["entry_byte_offset"] for row in shape["entry_candidates"]],
            [20, 254, 412, 648, 880, 1050, 1238, 1280, 2408, 3140, 3456],
        )
        self.assertEqual(
            [
                (
                    row["rank"],
                    row["entry_byte_offset"],
                    row["bytes_through_return"],
                    row["post_return_tail_bytes"],
                    row["thumb_decode_summary"]["instruction_count"],
                    row["thumb_decode_summary"]["pc_relative_load_count"],
                    row["thumb_decode_summary"]["branch_count"],
                    row["thumb_decode_summary"]["terminal_instruction"],
                )
                for row in shape["ranked_entry_pull_through_queue"]
            ][:4],
            [
                (1, 1238, 32, 10, 12, 3, 3, "pop {r1, pc}"),
                (2, 254, 158, 0, 61, 4, 17, "pop {r4, r5, r6, pc}"),
                (3, 880, 170, 0, 65, 5, 19, "pop {r4, r5, r6, pc}"),
                (4, 1050, 188, 0, 72, 5, 21, "pop {r4, r5, r6, pc}"),
            ],
        )
        self.assertEqual(
            [
                (row["rank"], row["entry_byte_offset"], row["bytes_through_return"])
                for row in shape["ranked_entry_pull_through_queue"]
            ][4:],
            [
                (5, 20, 216),
                (6, 412, 220),
                (7, 648, 232),
                (8, 3140, 308),
                (9, 2408, 330),
                (10, 1280, 1118),
            ],
        )
        self.assertEqual(
            shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 10,
                "semantic_model_count": 1,
                "semantic_model_ranks": [1],
                "semantic_frontier_count": 9,
                "semantic_frontier_ranks": [2, 3, 4, 5, 6, 7, 8, 9, 10],
                "semantic_frontier_kind_counts": {
                    "gated_dynamic_path_query_extended_output_returns_zero": 1,
                    "gated_dynamic_path_normalize_iterative_query_dump_returns_zero": 1,
                    "gated_dynamic_path_normalize_query_persist_returns_zero": 1,
                    "gated_path_component_filter_join_returns_status": 1,
                    "gated_stack_path_builder_extended_output_returns_zero": 1,
                    "gated_stack_path_builder_returns_zero": 1,
                    "gated_stack_path_builder_status_log_returns_zero": 1,
                    "gated_two_token_path_compare_update_returns_zero": 1,
                    "storage_context_metrics_log_returns_zero": 1,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 10,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertNotIn(
            "instructions",
            shape["ranked_entry_pull_through_queue"][1][
                "thumb_decode_summary"],
        )
        self.assertEqual(
            [
                (
                    row["semantic_frontier"]["kind"],
                    row["semantic_frontier"]["stack_frame_bytes"],
                    row["semantic_frontier"]["variant_log_literal"],
                    row["semantic_frontier"]["variant_success_call"],
                    row["semantic_frontier"]["fallback_call"],
                    row["semantic_frontier"]["extra_output_buffer_offset"],
                )
                for row in shape["ranked_entry_pull_through_queue"][1:5]
            ],
            [
                (
                    "gated_stack_path_builder_returns_zero",
                    0x104,
                    None,
                    0x00497A96,
                    None,
                    None,
                ),
                (
                    "gated_stack_path_builder_status_log_returns_zero",
                    0x104,
                    0x0076FDD8,
                    0x00497C7C,
                    None,
                    None,
                ),
                (
                    "gated_stack_path_builder_extended_output_returns_zero",
                    0x158,
                    0x0076FDD8,
                    0x00497AB4,
                    0x00497AF0,
                    0x104,
                ),
                (
                    "gated_dynamic_path_query_extended_output_returns_zero",
                    0x118,
                    None,
                    0x00497AB4,
                    0x00497AF0,
                    4,
                ),
            ],
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][4][
                    "semantic_frontier"][key]
                for key in (
                    "input_context_register",
                    "dynamic_segment_call",
                    "path_join_buffer_offset",
                    "path_join_buffer_bytes",
                    "query_output_buffer_offset",
                    "query_output_buffer_bytes",
                    "query_success_call",
                )
            },
            {
                "input_context_register": "r2",
                "dynamic_segment_call": 0x0054C91C,
                "path_join_buffer_offset": 0x44,
                "path_join_buffer_bytes": 0x80,
                "query_output_buffer_offset": 0xC4,
                "query_output_buffer_bytes": 0x40,
                "query_success_call": 0x00497B60,
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][5][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "input_output_buffer_register",
                    "stack_frame_bytes",
                    "scratch_buffer_bytes",
                    "component_vector_offset",
                    "max_component_count",
                    "delimiter_literal",
                    "skip_component_literals",
                    "tokenizer_call",
                    "compare_call",
                    "append_call",
                    "empty_path_fill_call",
                    "overflow_return_value",
                    "implementation_readiness",
                )
            },
            {
                "kind": "gated_path_component_filter_join_returns_status",
                "input_output_buffer_register": "r0",
                "stack_frame_bytes": 0x4FC,
                "scratch_buffer_bytes": 0xFF,
                "component_vector_offset": 0x100,
                "max_component_count": 0xFF,
                "delimiter_literal": "/",
                "skip_component_literals": [".", ".."],
                "tokenizer_call": 0x0055C8A4,
                "compare_call": 0x00434AEC,
                "append_call": 0x0052FCA0,
                "empty_path_fill_call": 0x00455560,
                "overflow_return_value": -1,
                "implementation_readiness":
                    "needs_path_component_filter_semantics",
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][6][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "normalizer_call",
                    "query_prepare_call",
                    "query_commit_call",
                    "primary_literal",
                    "path_error_log_literal",
                    "path_format_literal",
                    "raw_path_buffer_offset",
                    "normalized_path_buffer_offset",
                    "copy_back_bytes",
                    "implementation_readiness",
                )
            },
            {
                "kind": "gated_dynamic_path_normalize_query_persist_returns_zero",
                "normalizer_call": 0x00546AC8,
                "query_prepare_call": 0x00497C86,
                "query_commit_call": 0x00497D18,
                "primary_literal": 0x200031B4,
                "path_error_log_literal": 0x00782F40,
                "path_format_literal": 0x0078E13C,
                "raw_path_buffer_offset": 0x13C,
                "normalized_path_buffer_offset": 0x3C,
                "copy_back_bytes": 0x80,
                "implementation_readiness":
                    "needs_normalize_query_persist_semantics",
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][7][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "context_pointer",
                    "open_context_call",
                    "metrics_buffer_bytes",
                    "query_metrics_call",
                    "query_metrics_selector",
                    "capacity_base_constant",
                    "capacity_bias_constant",
                    "capacity_helper_call",
                    "log_literal_count",
                    "percent_warning_threshold",
                    "percent_error_threshold",
                    "implementation_readiness",
                )
            },
            {
                "kind": "storage_context_metrics_log_returns_zero",
                "context_pointer": 0x20074ABC,
                "open_context_call": 0x00498736,
                "metrics_buffer_bytes": 0x10,
                "query_metrics_call": 0x004985A0,
                "query_metrics_selector": 0x0057F531,
                "capacity_base_constant": 0x70800,
                "capacity_bias_constant": 0x0C74,
                "capacity_helper_call": 0x0049861A,
                "log_literal_count": 18,
                "percent_warning_threshold": 0x4C,
                "percent_error_threshold": 0x5B,
                "implementation_readiness": "needs_storage_metrics_semantics",
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][8][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "query_open_call",
                    "query_prepare_call",
                    "query_record_call",
                    "query_close_call",
                    "iterator_begin_call",
                    "iterator_next_call",
                    "dump_build_call",
                    "raw_path_buffer_offset",
                    "normalized_path_buffer_offset",
                    "dump_buffer_bytes",
                    "implementation_readiness",
                )
            },
            {
                "kind":
                    "gated_dynamic_path_normalize_iterative_query_dump_returns_zero",
                "query_open_call": 0x00497AAA,
                "query_prepare_call": 0x00497AB4,
                "query_record_call": 0x00497B60,
                "query_close_call": 0x00497AF0,
                "iterator_begin_call": 0x0055D46E,
                "iterator_next_call": 0x0055D598,
                "dump_build_call": 0x0055D628,
                "raw_path_buffer_offset": 0x34C,
                "normalized_path_buffer_offset": 0x24C,
                "dump_buffer_bytes": 0x10,
                "implementation_readiness":
                    "needs_iterative_query_dump_semantics",
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][9][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "stack_frame_bytes",
                    "token_count",
                    "token_length_limit",
                    "first_token_buffer_offset",
                    "second_token_buffer_offset",
                    "first_normalized_path_buffer_offset",
                    "second_normalized_path_buffer_offset",
                    "query_open_call",
                    "query_update_call",
                    "debug_log_call",
                    "implementation_readiness",
                )
            },
            {
                "kind": "gated_two_token_path_compare_update_returns_zero",
                "stack_frame_bytes": 0x91C,
                "token_count": 2,
                "token_length_limit": 0xFF,
                "first_token_buffer_offset": 0x81C,
                "second_token_buffer_offset": 0x71C,
                "first_normalized_path_buffer_offset": 0x420,
                "second_normalized_path_buffer_offset": 0x31C,
                "query_open_call": 0x00497AAA,
                "query_update_call": 0x00497AA0,
                "debug_log_call": 0x00405594,
                "implementation_readiness":
                    "needs_two_token_path_update_semantics",
            },
        )
        self.assertEqual(
            {
                key: shape["ranked_entry_pull_through_queue"][1][
                    "semantic_frontier"][key]
                for key in (
                    "gate_pointer",
                    "primary_literal",
                    "overflow_log_literal",
                    "final_call_context",
                    "implementation_readiness",
                )
            },
            {
                "gate_pointer": 0x200746A8,
                "primary_literal": 0x200031B4,
                "overflow_log_literal": 0x0078272C,
                "final_call_context": 0x20071AC8,
                "implementation_readiness": "needs_path_helper_semantics",
            },
        )
        self.assertEqual(
            shape["next_entry_pull_through_candidate"],
            {
                "entry_halfword_index": 619,
                "entry_byte_offset": 1238,
                "entry_address": 0x00546E02,
                "prologue_halfword": "0xb580",
                "next_entry_halfword_index": 640,
                "next_entry_address": 0x00546E2C,
                "span_to_next_entry_bytes": 42,
                "return_halfword_index": 634,
                "return_byte_offset": 1268,
                "return_address": 0x00546E20,
                "return_halfword": "0xbd02",
                "bytes_through_return": 32,
                "post_return_tail_bytes": 10,
                "post_return_tail_halfwords": [
                    "0x0000",
                    "0x7325",
                    "0x0000",
                    "0x002f",
                    "0x0000",
                ],
                "overlaps_next_entry": False,
                "has_local_return": True,
                "rank": 1,
                "status": "requires_c_pull_through",
                "implementation_readiness": "bounded_local_return_chunk",
                "thumb_decode": {
                    "available": True,
                    "instruction_count": 12,
                    "decoded_byte_count": 32,
                    "pc_relative_load_count": 3,
                    "branch_count": 3,
                    "call_targets": ["#0x43b40e"],
                    "literal_pool_references": [
                        {
                            "instruction_address": 0x00546E04,
                            "register": "r0",
                            "pc_base": 0x00546E08,
                            "literal_address": 0x00547290,
                            "image_offset": 0x00147290,
                            "word": 0x200746A8,
                        },
                        {
                            "instruction_address": 0x00546E12,
                            "register": "r1",
                            "pc_base": 0x00546E14,
                            "literal_address": 0x005473E4,
                            "image_offset": 0x001473E4,
                            "word": 0x200031B4,
                        },
                        {
                            "instruction_address": 0x00546E16,
                            "register": "r0",
                            "pc_base": 0x00546E18,
                            "literal_address": 0x00547960,
                            "image_offset": 0x00147960,
                            "word": 0x0078E144,
                        },
                    ],
                    "terminal_instruction": "pop {r1, pc}",
                    "instructions": [
                        {
                            "address": 0x00546E02,
                            "bytes": "80b5",
                            "mnemonic": "push",
                            "op_str": "{r7, lr}",
                        },
                        {
                            "address": 0x00546E04,
                            "bytes": "dff88804",
                            "mnemonic": "ldr.w",
                            "op_str": "r0, [pc, #0x488]",
                        },
                        {
                            "address": 0x00546E08,
                            "bytes": "0068",
                            "mnemonic": "ldr",
                            "op_str": "r0, [r0]",
                        },
                        {
                            "address": 0x00546E0A,
                            "bytes": "0128",
                            "mnemonic": "cmp",
                            "op_str": "r0, #1",
                        },
                        {
                            "address": 0x00546E0C,
                            "bytes": "01d0",
                            "mnemonic": "beq",
                            "op_str": "#0x546e12",
                        },
                        {
                            "address": 0x00546E0E,
                            "bytes": "0020",
                            "mnemonic": "movs",
                            "op_str": "r0, #0",
                        },
                        {
                            "address": 0x00546E10,
                            "bytes": "06e0",
                            "mnemonic": "b",
                            "op_str": "#0x546e20",
                        },
                        {
                            "address": 0x00546E12,
                            "bytes": "dff8d015",
                            "mnemonic": "ldr.w",
                            "op_str": "r1, [pc, #0x5d0]",
                        },
                        {
                            "address": 0x00546E16,
                            "bytes": "dff8480b",
                            "mnemonic": "ldr.w",
                            "op_str": "r0, [pc, #0xb48]",
                        },
                        {
                            "address": 0x00546E1A,
                            "bytes": "f4f6f8fa",
                            "mnemonic": "bl",
                            "op_str": "#0x43b40e",
                        },
                        {
                            "address": 0x00546E1E,
                            "bytes": "0020",
                            "mnemonic": "movs",
                            "op_str": "r0, #0",
                        },
                        {
                            "address": 0x00546E20,
                            "bytes": "02bd",
                            "mnemonic": "pop",
                            "op_str": "{r1, pc}",
                        },
                    ],
                },
                "semantic_model": {
                    "available": True,
                    "source": (
                        "components/apollo_main/core_overlay/"
                        "runtime_liblc3_am115_semantic_model.c"
                    ),
                    "test": "tests/test_runtime_liblc3_am115_semantic_model.py",
                    "function": "open_cfw_am115_0x546e02_semantic_model",
                    "kind": "gated_literal_call_returns_zero",
                    "entry_address": 0x00546E02,
                    "gate_pointer": 0x200746A8,
                    "call_r0": 0x0078E144,
                    "call_r1": 0x200031B4,
                    "call_target": 0x0043B40E,
                    "return_value": 0,
                    "firmware_routing_status": "not_yet_routed_into_overlay",
                },
            },
        )
        next_shape = largest["next_blocked_function_shape"]
        self.assertEqual(
            (
                next_shape["directive_halfword_count"],
                next_shape["directive_byte_count"],
                next_shape["first_prologue_halfword_index"],
                next_shape["prefix_before_first_prologue_halfwords"],
                next_shape["push_like_prologue_count"],
                next_shape["return_like_count"],
                next_shape["entry_candidate_count"],
                next_shape["bounded_local_return_entry_count"],
                next_shape["unbounded_or_overlapping_entry_count"],
            ),
            (966, 1932, 130, 130, 13, 20, 13, 12, 1),
        )
        self.assertEqual(
            [
                (
                    row["rank"],
                    row["entry_address"],
                    row["entry_byte_offset"],
                    row["bytes_through_return"],
                    row["thumb_decode_summary"]["instruction_count"],
                    row["thumb_decode_summary"]["terminal_instruction"],
                )
                for row in next_shape["ranked_entry_pull_through_queue"][:4]
            ],
            [
                (1, 0x00545EC4, 428, 10, 4, "pop {r0, pc}"),
                (2, 0x005463F8, 1760, 14, 6, "pop {r1, pc}"),
                (3, 0x00546406, 1774, 14, 6, "pop {r1, pc}"),
                (4, 0x00545E1C, 260, 14, 5, "pop {r0, pc}"),
            ],
        )
        self.assertEqual(
            next_shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 12,
                "semantic_model_count": 0,
                "semantic_model_ranks": [],
                "semantic_frontier_count": 12,
                "semantic_frontier_ranks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "semantic_frontier_kind_counts": {
                    "bounded_buffer_read_updates_read_cursor": 1,
                    "bounded_buffer_write_updates_write_cursor": 1,
                    "fixed_type_literal_event_call": 1,
                    "guarded_ring_descriptor_initialize": 1,
                    "literal_source_copy_returns_zero": 1,
                    "mode_set_delay_flush_returns_zero": 2,
                    "optional_callback_then_free_and_scheduler_cleanup": 1,
                    "ring_distance_from_triple_word_state": 1,
                    "string_cursor_advance_or_default_returns_pointer": 1,
                    "u16_argument_tail_call_wrapper": 1,
                    "zero_zero_service_call_returns_zero": 1,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 12,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertEqual(
            next_shape["ranked_entry_pull_through_queue"][0][
                "semantic_frontier"],
            {
                "available": True,
                "kind": "u16_argument_tail_call_wrapper",
                "entry_address": 0x00545EC4,
                "argument_register": "r1",
                "argument_transform": "uxth",
                "call_target": 0x00486876,
                "return_register_passthrough": "r0",
                "implementation_readiness": "needs_tail_call_wrapper_semantics",
                "firmware_routing_status": "not_yet_routed_into_overlay",
            },
        )
        self.assertEqual(
            [
                row["semantic_frontier"]["kind"]
                for row in next_shape["ranked_entry_pull_through_queue"][:6]
            ],
            [
                "u16_argument_tail_call_wrapper",
                "zero_zero_service_call_returns_zero",
                "literal_source_copy_returns_zero",
                "fixed_type_literal_event_call",
                "mode_set_delay_flush_returns_zero",
                "mode_set_delay_flush_returns_zero",
            ],
        )
        self.assertEqual(
            [
                row["semantic_frontier"]["kind"]
                for row in next_shape["ranked_entry_pull_through_queue"][6:]
            ],
            [
                "string_cursor_advance_or_default_returns_pointer",
                "optional_callback_then_free_and_scheduler_cleanup",
                "ring_distance_from_triple_word_state",
                "bounded_buffer_write_updates_write_cursor",
                "bounded_buffer_read_updates_read_cursor",
                "guarded_ring_descriptor_initialize",
            ],
        )
        third_shape = largest["third_blocked_function_shape"]
        self.assertEqual(
            (
                third_shape["directive_halfword_count"],
                third_shape["directive_byte_count"],
                third_shape["entry_candidate_count"],
                third_shape["bounded_local_return_entry_count"],
                third_shape["unbounded_or_overlapping_entry_count"],
            ),
            (476, 952, 2, 2, 0),
        )
        self.assertEqual(
            third_shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 2,
                "semantic_model_count": 0,
                "semantic_model_ranks": [],
                "semantic_frontier_count": 2,
                "semantic_frontier_ranks": [1, 2],
                "semantic_frontier_kind_counts": {
                    "retry_transaction_fill_compact_result": 1,
                    "u8_status_query_with_debug_logs": 1,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 2,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertEqual(
            [
                (
                    row["rank"],
                    row["entry_address"],
                    row["bytes_through_return"],
                    row["semantic_frontier"]["kind"],
                )
                for row in third_shape["ranked_entry_pull_through_queue"]
            ],
            [
                (1, 0x0054595C, 224, "u8_status_query_with_debug_logs"),
                (2, 0x00545A60, 280, "retry_transaction_fill_compact_result"),
            ],
        )
        fourth_shape = largest["fourth_blocked_function_shape"]
        self.assertEqual(
            (
                fourth_shape["directive_halfword_count"],
                fourth_shape["directive_byte_count"],
                fourth_shape["push_like_prologue_count"],
                fourth_shape["return_like_count"],
                fourth_shape["first_return_halfword_index"],
                fourth_shape["entry_candidate_count"],
                fourth_shape["bounded_local_return_entry_count"],
            ),
            (260, 520, 0, 1, 94, 0, 0),
        )
        self.assertEqual(fourth_shape["ranked_entry_pull_through_queue"], [])
        self.assertEqual(
            {
                key: fourth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "entry_address",
                    "uses_existing_stack_frame",
                    "retry_limit",
                    "result_pointer_register",
                    "transaction_call",
                    "cleanup_call",
                    "short_read_threshold",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_retry_transaction_tail_fill_u16_result",
                "entry_address": 0x00544D60,
                "uses_existing_stack_frame": True,
                "retry_limit": 3,
                "result_pointer_register": "r5",
                "transaction_call": 0x00544532,
                "cleanup_call": 0x00544660,
                "short_read_threshold": 2,
                "implementation_readiness": "needs_retry_tail_semantics",
            },
        )
        fifth_shape = largest["fifth_blocked_function_shape"]
        self.assertEqual(
            (
                fifth_shape["directive_halfword_count"],
                fifth_shape["directive_byte_count"],
                fifth_shape["entry_candidate_count"],
                fifth_shape["bounded_local_return_entry_count"],
                fifth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (219, 438, 5, 4, 1),
        )
        self.assertEqual(
            fifth_shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 4,
                "semantic_model_count": 0,
                "semantic_model_ranks": [],
                "semantic_frontier_count": 4,
                "semantic_frontier_ranks": [1, 2, 3, 4],
                "semantic_frontier_kind_counts": {
                    "device_state_format_buffer_returns_pointer": 1,
                    "literal_registration_burst": 1,
                    "status_byte_string_selector": 1,
                    "u16_probe_format_write_returns_zero": 1,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 4,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertEqual(
            [
                (
                    row["rank"],
                    row["entry_address"],
                    row["semantic_frontier"]["kind"],
                )
                for row in fifth_shape["ranked_entry_pull_through_queue"]
            ],
            [
                (1, 0x00546622, "u16_probe_format_write_returns_zero"),
                (2, 0x005466EC, "status_byte_string_selector"),
                (3, 0x00546646, "literal_registration_burst"),
                (4, 0x00546722, "device_state_format_buffer_returns_pointer"),
            ],
        )
        sixth_shape = largest["sixth_blocked_function_shape"]
        self.assertEqual(
            (
                sixth_shape["directive_halfword_count"],
                sixth_shape["directive_byte_count"],
                sixth_shape["entry_candidate_count"],
                sixth_shape["bounded_local_return_entry_count"],
                sixth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (168, 336, 3, 2, 1),
        )
        self.assertEqual(
            sixth_shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 2,
                "semantic_model_count": 0,
                "semantic_model_ranks": [],
                "semantic_frontier_count": 2,
                "semantic_frontier_ranks": [1, 2],
                "semantic_frontier_kind_counts": {
                    "dynamic_segment_command_dispatch_returns_zero": 2,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 2,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertEqual(
            [
                (
                    row["entry_address"],
                    row["semantic_frontier"]["match_length"],
                    row["semantic_frontier"]["action_kind"],
                    row["semantic_frontier"]["action_call"],
                )
                for row in sixth_shape["ranked_entry_pull_through_queue"]
            ],
            [
                (0x0054657A, 6, "no_arg_call", 0x004DA9BC),
                (0x0054651C, 2, "mode_call", 0x005576BA),
            ],
        )
        seventh_shape = largest["seventh_blocked_function_shape"]
        self.assertEqual(
            (
                seventh_shape["directive_halfword_count"],
                seventh_shape["directive_byte_count"],
                seventh_shape["first_prologue_halfword_index"],
                seventh_shape["prefix_before_first_prologue_halfwords"],
                seventh_shape["entry_candidate_count"],
                seventh_shape["bounded_local_return_entry_count"],
                seventh_shape["unbounded_or_overlapping_entry_count"],
            ),
            (167, 334, 95, 95, 1, 0, 1),
        )
        self.assertEqual(
            {
                key: seventh_shape["entry_candidates"][0][key]
                for key in (
                    "entry_address",
                    "has_local_return",
                    "return_address",
                    "span_to_next_entry_bytes",
                )
            },
            {
                "entry_address": 0x005457B4,
                "has_local_return": False,
                "return_address": None,
                "span_to_next_entry_bytes": 144,
            },
        )
        self.assertEqual(
            {
                key: seventh_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "embedded_entry_address",
                    "embedded_query_call",
                    "embedded_timeout",
                    "implementation_readiness",
                )
            },
            {
                "kind": "split_status_query_debug_tail_and_embedded_probe",
                "uses_existing_stack_frame": True,
                "embedded_entry_address": 0x005457B4,
                "embedded_query_call": 0x00544E98,
                "embedded_timeout": 0xC8,
                "implementation_readiness": "needs_split_status_query_semantics",
            },
        )
        eighth_shape = largest["eighth_blocked_function_shape"]
        self.assertEqual(
            (
                eighth_shape["directive_halfword_count"],
                eighth_shape["directive_byte_count"],
                eighth_shape["first_prologue_halfword_index"],
                eighth_shape["entry_candidate_count"],
                eighth_shape["bounded_local_return_entry_count"],
                eighth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (151, 302, 29, 2, 1, 1),
        )
        self.assertEqual(
            eighth_shape["ranked_entry_semantic_rollup"],
            {
                "ranked_entry_count": 1,
                "semantic_model_count": 0,
                "semantic_model_ranks": [],
                "semantic_frontier_count": 1,
                "semantic_frontier_ranks": [1],
                "semantic_frontier_kind_counts": {
                    "u8_status_query_with_debug_logs": 1,
                },
                "decode_only_count": 0,
                "decode_only_ranks": [],
                "classified_rank_count": 1,
                "implementation_readiness": "complete_semantic_frontier",
            },
        )
        self.assertEqual(
            [
                {
                    key: candidate[key]
                    for key in (
                        "entry_address",
                        "has_local_return",
                        "return_address",
                        "span_to_next_entry_bytes",
                    )
                }
                for candidate in eighth_shape["entry_candidates"]
            ],
            [
                {
                    "entry_address": 0x00545438,
                    "has_local_return": True,
                    "return_address": 0x005454FE,
                    "span_to_next_entry_bytes": 204,
                },
                {
                    "entry_address": 0x00545504,
                    "has_local_return": False,
                    "return_address": None,
                    "span_to_next_entry_bytes": 40,
                },
            ],
        )
        self.assertEqual(
            {
                key: eighth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "entry_address",
                    "query_call",
                    "success_status_value",
                )
            },
            {
                "kind": "u8_status_query_with_debug_logs",
                "entry_address": 0x00545438,
                "query_call": 0x00544850,
                "success_status_value": 1,
            },
        )
        self.assertEqual(
            {
                key: eighth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "first_embedded_entry_address",
                    "second_embedded_entry_address",
                    "implementation_readiness",
                )
            },
            {
                "kind": "split_u8_status_query_tail_and_embedded_probe_pair",
                "first_embedded_entry_address": 0x00545438,
                "second_embedded_entry_address": 0x00545504,
                "implementation_readiness": (
                    "needs_split_u8_status_probe_semantics"
                ),
            },
        )
        ninth_shape = largest["ninth_blocked_function_shape"]
        self.assertEqual(
            (
                ninth_shape["directive_halfword_count"],
                ninth_shape["directive_byte_count"],
                ninth_shape["push_like_prologue_count"],
                ninth_shape["return_like_count"],
                ninth_shape["entry_candidate_count"],
                ninth_shape["ranked_entry_semantic_rollup"][
                    "implementation_readiness"],
            ),
            (111, 222, 0, 0, 0, "complete_semantic_frontier"),
        )
        self.assertEqual(
            {
                key: ninth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "retry_service_call",
                    "read_call",
                    "cleanup_call",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_retry_read_status_tail_with_cleanup",
                "uses_existing_stack_frame": True,
                "retry_service_call": 0x00543B0C,
                "read_call": 0x00543D26,
                "cleanup_call": 0x00544660,
                "implementation_readiness": (
                    "needs_retry_read_status_tail_semantics"
                ),
            },
        )
        tenth_shape = largest["tenth_blocked_function_shape"]
        self.assertEqual(
            (
                tenth_shape["directive_halfword_count"],
                tenth_shape["directive_byte_count"],
                tenth_shape["push_like_prologue_count"],
                tenth_shape["return_like_count"],
                tenth_shape["entry_candidate_count"],
                tenth_shape["branch_like_halfword_count"],
            ),
            (103, 206, 0, 0, 0, 8),
        )
        self.assertEqual(
            {
                key: tenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "status_output_register",
                    "cleanup_call",
                    "failure_return_value",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_u16_status_pack_tail_with_cleanup",
                "uses_existing_stack_frame": True,
                "status_output_register": "r5",
                "cleanup_call": 0x00544660,
                "failure_return_value": -1,
                "implementation_readiness": (
                    "needs_u16_status_pack_tail_semantics"
                ),
            },
        )
        eleventh_shape = largest["eleventh_blocked_function_shape"]
        self.assertEqual(
            (
                eleventh_shape["directive_halfword_count"],
                eleventh_shape["directive_byte_count"],
                eleventh_shape["push_like_prologue_count"],
                eleventh_shape["return_like_count"],
                eleventh_shape["first_return_halfword_index"],
                eleventh_shape["post_first_return_halfword_count"],
                eleventh_shape["entry_candidate_count"],
            ),
            (100, 200, 0, 1, 96, 3, 0),
        )
        self.assertEqual(
            {
                key: eleventh_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "retry_limit",
                    "transaction_call",
                    "cleanup_call",
                    "terminal_return_halfword_index",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_retry_transaction_tail_fill_u8_result",
                "uses_existing_stack_frame": True,
                "retry_limit": 3,
                "transaction_call": 0x00544532,
                "cleanup_call": 0x00544660,
                "terminal_return_halfword_index": 96,
                "implementation_readiness": (
                    "needs_retry_transaction_u8_tail_semantics"
                ),
            },
        )
        twelfth_shape = largest["twelfth_blocked_function_shape"]
        self.assertEqual(
            (
                twelfth_shape["directive_halfword_count"],
                twelfth_shape["directive_byte_count"],
                twelfth_shape["push_like_prologue_count"],
                twelfth_shape["return_like_count"],
                twelfth_shape["branch_like_halfword_count"],
                twelfth_shape["entry_candidate_count"],
            ),
            (94, 188, 0, 0, 8, 0),
        )
        self.assertEqual(
            {
                key: twelfth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "filter_join_call",
                    "filter_join_call_count",
                    "primary_path_stack_offset",
                    "secondary_path_stack_offset",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_dual_path_filter_join_tail",
                "uses_existing_stack_frame": True,
                "filter_join_call": 0x00546AC8,
                "filter_join_call_count": 2,
                "primary_path_stack_offset": 0x520,
                "secondary_path_stack_offset": 0x41C,
                "implementation_readiness": (
                    "needs_dual_path_filter_join_tail_semantics"
                ),
            },
        )
        thirteenth_shape = largest["thirteenth_blocked_function_shape"]
        self.assertEqual(
            (
                thirteenth_shape["directive_halfword_count"],
                thirteenth_shape["directive_byte_count"],
                thirteenth_shape["push_like_prologue_count"],
                thirteenth_shape["return_like_count"],
                thirteenth_shape["branch_like_halfword_count"],
                thirteenth_shape["entry_candidate_count"],
            ),
            (91, 182, 0, 0, 7, 0),
        )
        self.assertEqual(
            {
                key: thirteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "preflight_call",
                    "transaction_start_call",
                    "success_tail_entry",
                    "implementation_readiness",
                )
            },
            {
                "kind": (
                    "prologueless_transaction_setup_tail_to_retry_read_status"
                ),
                "uses_existing_stack_frame": True,
                "preflight_call": 0x00543AA8,
                "transaction_start_call": 0x00544462,
                "success_tail_entry": 0x00545320,
                "implementation_readiness": (
                    "needs_transaction_setup_tail_semantics"
                ),
            },
        )
        fourteenth_shape = largest["fourteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fourteenth_shape["directive_halfword_count"],
                fourteenth_shape["directive_byte_count"],
                fourteenth_shape["push_like_prologue_count"],
                fourteenth_shape["return_like_count"],
                fourteenth_shape["branch_like_halfword_count"],
                fourteenth_shape["entry_candidate_count"],
            ),
            (81, 162, 0, 0, 6, 0),
        )
        self.assertEqual(
            {
                key: fourteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "uses_existing_stack_frame",
                    "bounded_copy_call",
                    "joined_path_clear_call",
                    "continuation_tail_entry",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_dual_path_input_staging_tail",
                "uses_existing_stack_frame": True,
                "bounded_copy_call": 0x00401C04,
                "joined_path_clear_call": 0x00404104,
                "continuation_tail_entry": 0x005477AC,
                "implementation_readiness": (
                    "needs_dual_path_input_staging_tail_semantics"
                ),
            },
        )
        fifteenth_shape = largest["fifteenth_blocked_function_shape"]
        self.assertEqual(
            (
                fifteenth_shape["directive_halfword_count"],
                fifteenth_shape["directive_byte_count"],
                fifteenth_shape["first_prologue_halfword_index"],
                fifteenth_shape["prefix_before_first_prologue_halfwords"],
                fifteenth_shape["push_like_prologue_count"],
                fifteenth_shape["return_like_count"],
                fifteenth_shape["entry_candidate_count"],
                fifteenth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (53, 106, 11, 11, 1, 0, 1, 1),
        )
        self.assertEqual(
            {
                key: fifteenth_shape["entry_candidates"][0][key]
                for key in (
                    "entry_address",
                    "has_local_return",
                    "return_address",
                    "span_to_next_entry_bytes",
                )
            },
            {
                "entry_address": 0x00544D0C,
                "has_local_return": False,
                "return_address": None,
                "span_to_next_entry_bytes": 84,
            },
        )
        self.assertEqual(
            {
                key: fifteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "embedded_entry_address",
                    "prefix_literal_halfwords",
                    "stack_frame_bytes",
                    "null_input_return_value",
                    "implementation_readiness",
                )
            },
            {
                "kind": "literal_prefix_embedded_retry_search_entry",
                "embedded_entry_address": 0x00544D0C,
                "prefix_literal_halfwords": 11,
                "stack_frame_bytes": 0x30,
                "null_input_return_value": -1,
                "implementation_readiness": (
                    "needs_embedded_retry_search_entry_semantics"
                ),
            },
        )
        sixteenth_shape = largest["sixteenth_blocked_function_shape"]
        self.assertEqual(
            (
                sixteenth_shape["directive_halfword_count"],
                sixteenth_shape["directive_byte_count"],
                sixteenth_shape["first_prologue_halfword_index"],
                sixteenth_shape["push_like_prologue_count"],
                sixteenth_shape["return_like_count"],
                sixteenth_shape["first_return_halfword_index"],
                sixteenth_shape["post_first_return_halfword_count"],
                sixteenth_shape["entry_candidate_count"],
            ),
            (53, 106, 52, 1, 1, 42, 10, 1),
        )
        self.assertEqual(
            {
                key: sixteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "status_register",
                    "success_return_value",
                    "terminal_return_halfword_index",
                    "embedded_following_entry_address",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_u8_status_debug_return_tail",
                "status_register": "r5",
                "success_return_value": 0,
                "terminal_return_halfword_index": 42,
                "embedded_following_entry_address": 0x005456D4,
                "implementation_readiness": (
                    "needs_u8_status_debug_tail_semantics"
                ),
            },
        )
        seventeenth_shape = largest["seventeenth_blocked_function_shape"]
        self.assertEqual(
            (
                seventeenth_shape["directive_halfword_count"],
                seventeenth_shape["directive_byte_count"],
                seventeenth_shape["first_prologue_halfword_index"],
                seventeenth_shape["prefix_before_first_prologue_halfwords"],
                seventeenth_shape["push_like_prologue_count"],
                seventeenth_shape["return_like_count"],
                seventeenth_shape["entry_candidate_count"],
                seventeenth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (50, 100, 5, 5, 1, 0, 1, 1),
        )
        self.assertEqual(
            {
                key: seventeenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "embedded_entry_address",
                    "prefix_literal_halfwords",
                    "option_stack_offset",
                    "loop_index_register",
                    "implementation_readiness",
                )
            },
            {
                "kind": "literal_prefix_embedded_retry_option_initializer",
                "embedded_entry_address": 0x00545044,
                "prefix_literal_halfwords": 5,
                "option_stack_offset": 0x10,
                "loop_index_register": "r7",
                "implementation_readiness": (
                    "needs_embedded_retry_option_initializer_semantics"
                ),
            },
        )
        eighteenth_shape = largest["eighteenth_blocked_function_shape"]
        self.assertEqual(
            (
                eighteenth_shape["directive_halfword_count"],
                eighteenth_shape["directive_byte_count"],
                eighteenth_shape["push_like_prologue_count"],
                eighteenth_shape["return_like_count"],
                eighteenth_shape["branch_like_halfword_count"],
                eighteenth_shape["entry_candidate_count"],
            ),
            (48, 96, 0, 0, 4, 0),
        )
        self.assertEqual(
            {
                key: eighteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "selector_saved_register",
                    "clear_call",
                    "retry_search_call",
                    "query_timeout",
                    "success_tail_entry",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_u16_status_query_via_retry_search_tail",
                "selector_saved_register": "r5",
                "clear_call": 0x00404104,
                "retry_search_call": 0x00544D0C,
                "query_timeout": 0xC8,
                "success_tail_entry": 0x0054566E,
                "implementation_readiness": (
                    "needs_u16_status_retry_search_tail_semantics"
                ),
            },
        )
        nineteenth_shape = largest["nineteenth_blocked_function_shape"]
        self.assertEqual(
            (
                nineteenth_shape["directive_halfword_count"],
                nineteenth_shape["directive_byte_count"],
                nineteenth_shape["entry_candidate_count"],
                nineteenth_shape["bounded_local_return_entry_count"],
                nineteenth_shape["unbounded_or_overlapping_entry_count"],
                nineteenth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
            ),
            (40, 80, 2, 1, 1, 1),
        )
        self.assertEqual(
            {
                key: nineteenth_shape["ranked_entry_pull_through_queue"][0][
                    "semantic_frontier"][key]
                for key in (
                    "kind",
                    "entry_address",
                    "call_target",
                    "return_vfp_register",
                )
            },
            {
                "kind": "vfp_d0_d1_compare_wrapper",
                "entry_address": 0x00545C60,
                "call_target": 0x00545C74,
                "return_vfp_register": "d0",
            },
        )
        self.assertEqual(
            {
                key: nineteenth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "wrapper_entry_address",
                    "embedded_compare_entry_address",
                    "uses_vfp_registers",
                    "it_halfword_indexes",
                    "implementation_readiness",
                )
            },
            {
                "kind": "vfp_wrapper_and_embedded_u64_compare_body",
                "wrapper_entry_address": 0x00545C60,
                "embedded_compare_entry_address": 0x00545C74,
                "uses_vfp_registers": True,
                "it_halfword_indexes": [22, 28],
                "implementation_readiness": (
                    "needs_vfp_compare_wrapper_and_body_semantics"
                ),
            },
        )
        twentieth_shape = largest["twentieth_blocked_function_shape"]
        self.assertEqual(
            (
                twentieth_shape["directive_halfword_count"],
                twentieth_shape["directive_byte_count"],
                twentieth_shape["push_like_prologue_count"],
                twentieth_shape["return_like_count"],
                twentieth_shape["entry_candidate_count"],
                twentieth_shape["bounded_local_return_entry_count"],
                twentieth_shape["unbounded_or_overlapping_entry_count"],
                twentieth_shape["ranked_entry_semantic_rollup"][
                    "classified_rank_count"],
            ),
            (29, 58, 1, 1, 1, 0, 1, 0),
        )
        self.assertEqual(
            {
                key: twentieth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "tail_debug_call",
                    "embedded_status_entry_address",
                    "embedded_clear_call",
                    "authenticated_decompile_kind",
                    "implementation_readiness",
                )
            },
            {
                "kind": (
                    "split_debug_tail_literal_pool_and_embedded_status_setup"
                ),
                "tail_debug_call": 0x00404EBE,
                "embedded_status_entry_address": 0x00545890,
                "embedded_clear_call": 0x00404104,
                "authenticated_decompile_kind": "crc16_ccitt_byte_loop",
                "implementation_readiness": (
                    "needs_boundary_reconciliation_before_crc_or_status_semantics"
                ),
            },
        )
        twenty_first_shape = largest["twenty_first_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_first_shape["directive_halfword_count"],
                twenty_first_shape["directive_byte_count"],
                twenty_first_shape["push_like_prologue_count"],
                twenty_first_shape["return_like_count"],
                twenty_first_shape["entry_candidate_count"],
                twenty_first_shape["branch_like_halfword_count"],
            ),
            (25, 50, 0, 0, 0, 2),
        )
        self.assertEqual(
            {
                key: twenty_first_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "literal_load_count",
                    "log_format_call",
                    "debug_gate_checks",
                    "authenticated_decompile_calls",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_four_stage_debug_log_dispatch_tail",
                "literal_load_count": 3,
                "log_format_call": 0x00405594,
                "debug_gate_checks": 2,
                "authenticated_decompile_calls": [
                    0x0044122A,
                    0x00441238,
                    0x0044120E,
                    0x0044121C,
                ],
                "implementation_readiness": (
                    "needs_four_stage_debug_log_tail_semantics"
                ),
            },
        )
        twenty_second_shape = largest["twenty_second_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_second_shape["directive_halfword_count"],
                twenty_second_shape["directive_byte_count"],
                twenty_second_shape["push_like_prologue_count"],
                twenty_second_shape["return_like_count"],
                twenty_second_shape["entry_candidate_count"],
                twenty_second_shape["branch_like_halfword_count"],
            ),
            (20, 40, 0, 0, 0, 3),
        )
        self.assertEqual(
            {
                key: twenty_second_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "prefix_halfword_is_prior_wide_call_suffix",
                    "debug_emit_code",
                    "shared_return_tail_entry",
                    "authenticated_decompile_calls",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_compass_debug_tail_to_shared_return",
                "prefix_halfword_is_prior_wide_call_suffix": True,
                "debug_emit_code": 0x04800000,
                "shared_return_tail_entry": 0x0054566A,
                "authenticated_decompile_calls": [
                    0x0043D574,
                    0x0043D0CE,
                    0x0043D0CE,
                    0x0043CE9E,
                ],
                "implementation_readiness": (
                    "needs_compass_debug_tail_boundary_semantics"
                ),
            },
        )
        twenty_third_shape = largest["twenty_third_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_third_shape["directive_halfword_count"],
                twenty_third_shape["directive_byte_count"],
                twenty_third_shape["push_like_prologue_count"],
                twenty_third_shape["return_like_count"],
                twenty_third_shape["entry_candidate_count"],
                twenty_third_shape["branch_like_halfword_count"],
            ),
            (18, 36, 0, 0, 0, 1),
        )
        self.assertEqual(
            {
                key: twenty_third_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "condition_source",
                    "line_literal",
                    "debug_emit_code",
                    "authenticated_decompile_calls",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_condition_flag_debug_emit_tail",
                "condition_source": (
                    "incoming_negative_flag_or_debug_gate_bit29"
                ),
                "line_literal": 0x33A,
                "debug_emit_code": 0x10800000,
                "authenticated_decompile_calls": [0x0043D0CE, 0x0043CE9E],
                "implementation_readiness": (
                    "needs_condition_flag_debug_emit_tail_semantics"
                ),
            },
        )
        twenty_fourth_shape = largest["twenty_fourth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fourth_shape["directive_halfword_count"],
                twenty_fourth_shape["directive_byte_count"],
                twenty_fourth_shape["push_like_prologue_count"],
                twenty_fourth_shape["return_like_count"],
                twenty_fourth_shape["entry_candidate_count"],
                twenty_fourth_shape["branch_like_halfword_count"],
            ),
            (16, 32, 0, 0, 0, 1),
        )
        self.assertEqual(
            {
                key: twenty_fourth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "clear_call",
                    "query_call",
                    "query_selector",
                    "authenticated_decompile_kind",
                    "implementation_readiness",
                )
            },
            {
                "kind": (
                    "prologueless_status_query_setup_tail_with_decompile_conflict"
                ),
                "clear_call": 0x00404104,
                "query_call": 0x00544E98,
                "query_selector": 1,
                "authenticated_decompile_kind": (
                    "two_byte_affine_mixer_no_callees"
                ),
                "implementation_readiness": (
                    "needs_status_query_tail_boundary_reconciliation"
                ),
            },
        )
        twenty_fifth_shape = largest["twenty_fifth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_fifth_shape["directive_halfword_count"],
                twenty_fifth_shape["directive_byte_count"],
                twenty_fifth_shape["push_like_prologue_count"],
                twenty_fifth_shape["return_like_count"],
                twenty_fifth_shape["entry_candidate_count"],
                twenty_fifth_shape["unbounded_or_overlapping_entry_count"],
            ),
            (15, 30, 1, 1, 1, 1),
        )
        self.assertEqual(
            {
                key: twenty_fifth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "embedded_entry_address",
                    "authenticated_decompile_calls",
                    "boundary_conflict",
                    "implementation_readiness",
                )
            },
            {
                "kind": "split_return_literal_pool_and_embedded_two_call_entry",
                "embedded_entry_address": 0x005455E0,
                "authenticated_decompile_calls": [0x004411F2, 0x00441200],
                "boundary_conflict": (
                    "raw_helper_body_decodes_as_prior_return_tail_literal_pool_"
                    "and_embedded_following_prologue"
                ),
                "implementation_readiness": (
                    "needs_two_call_entry_boundary_reconciliation"
                ),
            },
        )
        twenty_sixth_shape = largest["twenty_sixth_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_sixth_shape["directive_halfword_count"],
                twenty_sixth_shape["directive_byte_count"],
                twenty_sixth_shape["push_like_prologue_count"],
                twenty_sixth_shape["return_like_count"],
                twenty_sixth_shape["entry_candidate_count"],
                twenty_sixth_shape["branch_like_halfword_count"],
            ),
            (6, 12, 0, 0, 0, 1),
        )
        self.assertEqual(
            {
                key: twenty_sixth_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "guard_branch_target",
                    "line_literal",
                    "authenticated_decompile_call",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_opacity_debug_literal_prefix",
                "guard_branch_target": 0x005455A8,
                "line_literal": 0x306,
                "authenticated_decompile_call": 0x0044BDEA,
                "implementation_readiness": (
                    "needs_opacity_debug_prefix_boundary_reconciliation"
                ),
            },
        )
        twenty_seventh_shape = largest["twenty_seventh_blocked_function_shape"]
        self.assertEqual(
            (
                twenty_seventh_shape["directive_halfword_count"],
                twenty_seventh_shape["directive_byte_count"],
                twenty_seventh_shape["push_like_prologue_count"],
                twenty_seventh_shape["return_like_count"],
                twenty_seventh_shape["entry_candidate_count"],
                twenty_seventh_shape["branch_like_halfword_count"],
            ),
            (5, 10, 0, 0, 0, 2),
        )
        self.assertEqual(
            {
                key: twenty_seventh_shape["function_semantic_frontier"][key]
                for key in (
                    "kind",
                    "tail_branch_target",
                    "authenticated_decompile_call",
                    "authenticated_context_offset",
                    "implementation_readiness",
                )
            },
            {
                "kind": "prologueless_retry_service_tail_branch_fragment",
                "tail_branch_target": 0x00544C96,
                "authenticated_decompile_call": 0x00544C78,
                "authenticated_context_offset": 0x10,
                "implementation_readiness": (
                    "needs_retry_service_tail_branch_semantics"
                ),
            },
        )
        self.assertEqual(
            {
                key: shape["entry_candidates"][0][key]
                for key in (
                    "entry_address",
                    "return_address",
                    "post_return_tail_bytes",
                )
            },
            {
                "entry_address": 0x00546940,
                "return_address": 0x00546A16,
                "post_return_tail_bytes": 18,
            },
        )
        self.assertEqual(
            {
                key: shape["entry_candidates"][-1][key]
                for key in (
                    "entry_address",
                    "return_address",
                    "post_return_tail_bytes",
                    "has_local_return",
                )
            },
            {
                "entry_address": 0x005476AC,
                "return_address": None,
                "post_return_tail_bytes": None,
                "has_local_return": False,
            },
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
