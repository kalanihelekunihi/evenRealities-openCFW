import unittest
from tools import analyze_g2_service_ancc as a

class G2ServiceAnccTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=a.analyze()
    def test_object(self):
        s=self.report["surface"]
        self.assertEqual((s["linked_functions"],s["body_bytes"],s["physical_bytes"]),(12,2340,2890))
        self.assertEqual((s["path_anchored_functions"],s["restored_non_anchor_functions"]),(6,6))
        self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(131,2,129))
    def test_ingress(self):
        s=self.report["surface"]
        self.assertEqual((s["direct_bl_entry_sites"],s["stored_interior_callback_pointers"]),(31,3))
        self.assertEqual((s["strict_interior_ingress"],s["raw_noncode_pseudo_bl"]),(0,6))
    def test_dependency_boundary(self):
        p=self.report["provider_boundary"]
        self.assertEqual((p["easylogger_calls"],p["cmsis_freertos_mutex_calls"],p["iar_dlib_calls"],p["closed_first_party_calls"]),(85,17,10,17))
        self.assertEqual((p["direct_ambiqsuite_ancc_calls"],p["embedded_ambiqsuite_ancc_definitions"]),(0,0))
        self.assertEqual(p["cmsis_freertos_commit"],"d213f261b5be6bb29a7cce8b84071706b72f4d53")
    def test_behavior_and_gate(self):
        self.assertEqual((self.report["behavior"]["fixed_record_count"],self.report["behavior"]["record_bytes"]),(10,0x304))
        self.assertTrue(self.report["behavior"]["mutex_protected"])
        self.assertFalse(self.report["production"]["production_routed"])

if __name__=="__main__":unittest.main()
