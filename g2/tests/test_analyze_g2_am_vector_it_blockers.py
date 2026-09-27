import json
import unittest

from tools import analyze_g2_am_vector_it_blockers as analyzer


class G2AmVectorItBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_vector_and_it_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["blocker_count"], 370)
        self.assertEqual(self.report["blocker_bytes"], 174916)
        self.assertEqual(self.report["it_blocker_count"], 119)
        self.assertEqual(self.report["vector_blocker_count"], 287)
        self.assertEqual(
            self.report["class_counts"],
            {
                "linear:it_block_requires_conditional_text_or_whole_body_source": {
                    "bytes": 12888,
                    "functions": 41,
                },
                "linear:it_block_requires_conditional_text_or_whole_body_source,vector_instruction_text_not_apple_clang_roundtrip_safe": {
                    "bytes": 5888,
                    "functions": 17,
                },
                "linear:vector_instruction_text_not_apple_clang_roundtrip_safe": {
                    "bytes": 30680,
                    "functions": 117,
                },
                "mixed:it_block_requires_conditional_text_or_whole_body_source": {
                    "bytes": 34522,
                    "functions": 42,
                },
                "mixed:it_block_requires_conditional_text_or_whole_body_source,vector_instruction_text_not_apple_clang_roundtrip_safe": {
                    "bytes": 47408,
                    "functions": 19,
                },
                "mixed:vector_instruction_text_not_apple_clang_roundtrip_safe": {
                    "bytes": 43530,
                    "functions": 134,
                },
            },
        )

    def test_vector_rows_have_vector_examples(self) -> None:
        vector_rows = [
            blocker for blocker in self.report["blockers"]
            if "vector_instruction_text_not_apple_clang_roundtrip_safe"
            in blocker["reasons"]
        ]
        self.assertTrue(all(blocker["vector_examples"] for blocker in vector_rows))

    def test_it_rows_have_it_offsets(self) -> None:
        it_rows = [
            blocker for blocker in self.report["blockers"]
            if "it_block_requires_conditional_text_or_whole_body_source"
            in blocker["reasons"]
        ]
        self.assertTrue(all(blocker["it_offsets"] for blocker in it_rows))

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
