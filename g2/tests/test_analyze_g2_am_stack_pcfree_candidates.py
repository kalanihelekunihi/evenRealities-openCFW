import json
import unittest

from tools import analyze_g2_am_stack_pcfree_candidates as analyzer


class G2AmStackPcFreeCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_candidate_census_is_pinned(self) -> None:
        self.assertEqual(self.report["candidate_count"], 0)
        self.assertEqual(self.report["candidate_bytes"], 0)
        for candidate in self.report["candidates"]:
            self.assertTrue(candidate["source"].startswith(
                "components/apollo_main/core_overlay/runtime_liblc3_am"))
            self.assertGreater(candidate["byte_length"], 0)
            self.assertEqual(
                candidate["byte_length"],
                sum(instruction["size"] for instruction in candidate["mnemonics"]),
            )
            texts = [instruction["text"] for instruction in candidate["mnemonics"]]
            self.assertTrue(any(
                text.split()[0].split(".")[0] in {
                    "push", "pop", "ldm", "stm", "stmdb"
                }
                for text in texts
            ))

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
