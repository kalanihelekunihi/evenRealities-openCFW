import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_frontier.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_frontier", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        corpus = MODULE.CORPUS
        if not (corpus / "SHA256SUMS").is_file():
            raise unittest.SkipTest("authenticated Apollo corpus unavailable")
        cls.report = MODULE.analyze()

    def test_census(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["retained_pb_service_paths"], 15)
        self.assertEqual(surface["anchored_functions"], 119)
        self.assertEqual(surface["anchored_body_bytes"], 40844)
        self.assertEqual(surface["corpus_functions"], 7370)
        self.assertEqual(surface["decompile_failures"], 0)

    def test_selected_frontier(self) -> None:
        selected = self.report["selected"]
        self.assertEqual(selected["path"], r"platform\protocols\pb_service_translate\pb_service_translate.c")
        self.assertEqual(selected["anchored_functions"], 4)
        self.assertEqual(selected["anchored_body_bytes"], 1324)
        self.assertEqual(selected["interval_lower_bound"], "[0x0059f53c,0x0059fa68)")

    def test_lower_bound_qualification(self) -> None:
        self.assertIn("lower bounds", self.report["qualification"])


if __name__ == "__main__":
    unittest.main()
