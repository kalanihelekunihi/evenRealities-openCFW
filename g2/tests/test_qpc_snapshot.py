import importlib.util
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "third_party/qpc/verify_snapshot.py"
SPEC = importlib.util.spec_from_file_location("verify_qpc_snapshot", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class QpcSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = MODULE.verify()

    def test_identity_and_host_compile(self):
        self.assertEqual(self.result["version"], "6.5.1")
        self.assertEqual(self.result["portable_sources"], 8)
        self.assertEqual(self.result["host_compile"], "pass")

    def test_target_state_is_explicit(self):
        self.assertIn(self.result["arc_target"], {"blocked_unavailable_reviewed_arc_compiler", "arc_objects_compiled_not_integrated"})
        self.assertFalse(self.result["production_routed"])


if __name__ == "__main__":
    unittest.main()
