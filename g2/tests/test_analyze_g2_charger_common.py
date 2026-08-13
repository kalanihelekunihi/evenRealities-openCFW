import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_charger_common.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_charger_common", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2ChargerCommonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 14,
            "body_bytes": 2764,
            "owned_noncode_bytes": 220,
            "physical_bytes": 2984,
            "direct_bl_entry_sites": 25,
            "exterior_bl_entry_sites": 10,
            "direct_body_calls": 157,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 6,
        })

    def test_runtime_and_wire_abi(self) -> None:
        self.assertEqual(self.report["abi"]["runtime_bytes"], 24)
        self.assertEqual(self.report["abi"]["soc_offset"], "0x10")
        self.assertEqual(self.report["abi"]["charging_offset"], "0x14")
        self.assertEqual(self.report["abi"]["wire_message_bytes"], 12)
        self.assertEqual(self.report["abi"]["service_id"], "0x0105")

    def test_retry_and_message_contract(self) -> None:
        self.assertEqual(self.report["behavior"]["initial_retry_polls"], [2, 4, 6, 8])
        self.assertEqual(self.report["behavior"]["initial_timeout_poll"], 16)
        self.assertEqual(self.report["behavior"]["near_full_charge_debounce_samples"], 4)
        self.assertEqual([
            self.report["behavior"]["notify_message_id"],
            self.report["behavior"]["response_message_id"],
            self.report["behavior"]["request_message_id"],
        ], [3, 2, 4])

    def test_candidate_is_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
