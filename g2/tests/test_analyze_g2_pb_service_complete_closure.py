import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_pb_service_complete_closure.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_pb_service_complete_closure", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2PbServiceCompleteClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_complete_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "retained_paths": 15, "linked_functions": 143,
            "body_bytes": 47644, "physical_bytes": 51744,
            "production_ownership_bytes": 6352, "non_body_owned_bytes": 4100,
        })

    def test_frontier_reconciliation(self) -> None:
        self.assertEqual(self.report["frontier_reconciliation"], {
            "anchored_functions": 119, "closed_linked_functions": 143,
            "restored_functions": 24, "anchored_body_bytes": 40844,
            "closed_body_bytes": 47644, "restored_body_bytes": 6800,
        })

    def test_qualification(self) -> None:
        self.assertEqual(self.report["qualification"], {
            "all_retained_paths_closed": True,
            "historical_source_inventory_complete": False,
            "production_routed_services": 4,
        })


if __name__ == "__main__":
    unittest.main()
