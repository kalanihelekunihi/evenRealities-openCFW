import unittest

from tools import analyze_g2_pt_protocol as analyzer


class G2PtProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyzer.analyze()

    def test_complete_object(self):
        surface = self.report["surface"]
        self.assertEqual((surface["linked_functions"], surface["body_bytes"], surface["physical_bytes"]), (73, 32866, 35524))
        self.assertEqual((surface["path_anchored_functions"], surface["restored_non_anchor_functions"]), (69, 4))

    def test_dispatch_and_ingress(self):
        surface = self.report["surface"]
        self.assertEqual((surface["indirect_body_calls"], surface["bounded_internal_dispatches"]), (1, 1))
        self.assertEqual((surface["direct_bl_entry_sites"], surface["stored_function_pointers"]), (30, 66))
        self.assertEqual((surface["unaligned_pseudo_bl"], surface["external_strict_interior_ingress"]), (4, 0))

    def test_provider_boundary(self):
        providers = self.report["provider_boundary"]
        self.assertEqual(
            (providers["easylogger_calls"], providers["cmsis_freertos_calls"], providers["freertos_kernel_calls"], providers["runtime_calls"], providers["mpaland_printf_calls"], providers["first_party_calls"]),
            (1280, 7, 1, 41, 1, 196),
        )
        self.assertIsNone(providers["historical_product_test_commit"])

    def test_no_embedded_reusable_code_or_production_route(self):
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
