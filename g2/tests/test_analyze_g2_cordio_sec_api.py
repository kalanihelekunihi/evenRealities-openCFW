import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_cordio_sec_api.py"
S = importlib.util.spec_from_file_location("g2_cordio_sec_api", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class CordioSecApiClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()

    def test_identity(self):
        self.assertEqual(self.result["identity"], {
            "component": "Packetcraft Cordio sec_api",
            "release": "r20.05c",
            "commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "license": "Apache-2.0",
            "disposition": "implemented-in-source; hardware-blocked",
            "first_party_even_backend": False,
        })

    def test_stock_boundary(self):
        self.assertEqual(self.result["stock"], {
            "functions": 20, "body_bytes": 1392, "retained_gap_bytes": 46, "physical_bytes": 1438,
        })

    def test_production_route(self):
        self.assertEqual(self.result["production"], {
            "production_routed": True,
            "source_functions": 20,
            "compiled_text_bytes": 1952,
            "alignment_bytes": 16,
            "strict_relocations": 65,
            "package_byte_identical": True,
            "placed_regions": 6193,
            "unresolved_regions": 2,
            "primitive_provider": "retained HCI/controller boundary",
            "hardware_validation": "blocked_unavailable_authorized_physical_evidence",
        })


if __name__ == "__main__":
    unittest.main()
