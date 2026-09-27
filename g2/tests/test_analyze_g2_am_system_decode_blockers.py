import json
import unittest

from tools import analyze_g2_am_system_decode_blockers as analyzer


class G2AmSystemDecodeBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_system_decode_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["blocker_count"], 21)
        self.assertEqual(self.report["blocker_bytes"], 1874)
        self.assertGreater(self.report["system_instruction_count"], 0)
        self.assertGreater(self.report["zero_halfword_count"], 0)

    def test_every_blocker_has_system_decode_evidence(self) -> None:
        self.assertTrue(all(
            blocker["system_instruction_count"] > 0
            for blocker in self.report["blockers"]
        ))

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
