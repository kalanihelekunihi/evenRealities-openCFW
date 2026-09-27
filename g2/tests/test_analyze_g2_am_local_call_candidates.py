import json
import unittest

from tools import analyze_g2_am_local_call_candidates as analyzer


class G2AmLocalCallCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_candidate_census_is_pinned(self) -> None:
        self.assertEqual(self.report["candidate_count"], 0)
        self.assertEqual(self.report["candidate_bytes"], 0)
        self.assertEqual(self.report["candidates"], [])

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
