import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_uled_mspi_common.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_uled_mspi_common", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2UledMspiCommonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()

    def test_surface(self) -> None:
        self.assertEqual(self.report["surface"], {
            "linked_functions": 13,
            "body_bytes": 2358,
            "owned_noncode_bytes": 238,
            "physical_bytes": 2596,
            "direct_bl_entry_sites": 30,
            "exterior_bl_entry_sites": 11,
            "direct_body_calls": 151,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 2,
        })

    def test_request_and_transfer_abi(self) -> None:
        self.assertEqual(self.report["abi"]["request_bytes"], 28)
        self.assertEqual(self.report["abi"]["request_offsets"]["data"], 20)
        self.assertEqual(self.report["abi"]["request_offsets"]["handle"], 24)
        self.assertEqual(self.report["abi"]["hal_transfer_bytes"], 24)
        self.assertEqual(self.report["abi"]["semaphore"], "0x20074534")
        self.assertEqual(self.report["abi"]["completion_status"], "0x200007ec")

    def test_modes_and_timeouts(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["blocking_timeout_us"], 1_000_000)
        self.assertEqual(behavior["async_timeout_ms"], 3000)
        self.assertEqual(behavior["interrupt_mask"], "0x00001a80")
        self.assertEqual(behavior["mspi_module"], 0)
        self.assertEqual(behavior["mspi_irq"], 20)
        self.assertEqual(behavior["mspi_irq_priority"], 4)

    def test_remains_analysis_only(self) -> None:
        self.assertIsNone(self.report["production"]["candidate"])
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
