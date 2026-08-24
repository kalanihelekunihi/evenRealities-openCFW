import unittest
from tools import analyze_g2_als as a

class G2AlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=a.analyze()
    def test_object(self):
        s=self.report["surface"]
        self.assertEqual((s["linked_functions"],s["body_bytes"],s["physical_bytes"]),(38,3858,4232))
        self.assertEqual((s["path_anchored_functions"],s["restored_non_anchor_functions"]),(9,29))
        self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(189,50,139))
    def test_ingress(self):
        s=self.report["surface"]
        self.assertEqual((s["direct_bl_entry_sites"],s["stored_function_pointers"]),(60,1))
        self.assertEqual((s["indirect_body_calls"],s["bounded_first_party_indirect_calls"]),(1,1))
        self.assertEqual((s["strict_interior_ingress"],s["unaligned_pseudo_bl"]),(0,1))
    def test_dependency_boundary(self):
        p=self.report["provider_boundary"]
        self.assertEqual((p["easylogger_calls"],p["cmsis_freertos_delay_calls"],p["runtime_calls"],p["closed_first_party_calls"],p["opt3007_adapter_calls"]),(105,1,4,23,6))
        self.assertIsNone(p["public_opt3007_software_commit"])
        self.assertTrue(p["opt3007_adapter_production_routed"])
    def test_gate(self):self.assertFalse(self.report["production"]["production_routed"])

if __name__=="__main__":unittest.main()
