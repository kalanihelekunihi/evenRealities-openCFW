import unittest
from tools import analyze_g2_drv_pdm as a

class G2DrvPdmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=a.analyze()
    def test_object(self):
        s=self.report["surface"]
        self.assertEqual((s["linked_functions"],s["body_bytes"],s["physical_bytes"]),(7,794,900))
        self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(51,4,47))
        self.assertEqual((s["stored_function_entry_pointers"],s["strict_interior_ingress"],s["raw_noncode_pseudo_bl"]),(1,0,1))
    def test_upstream_seam(self):
        p=self.report["provider_boundary"]
        self.assertEqual((p["ambiqsuite_pdm_calls"],p["ambiqsuite_pdm_apis"]),(19,14))
        self.assertEqual(p["ambiqsuite_selected_commit"],"5efc0228528a8adce5eae0d226fac85d2551eb3b")
        self.assertEqual(p["ambiqsuite_source_git_blob"],"23a440bfd6121509b0586f0afe1990fcf59dd8fb")
        self.assertFalse(p["private_generating_commit_recoverable"])
    def test_irq_and_samples(self):
        self.assertTrue(self.report["behavior"]["pdm0_irq_handler"])
        self.assertEqual((self.report["behavior"]["output_samples"],self.report["behavior"]["output_bytes"]),(160,320))
        self.assertEqual(len(self.report["identity"]["embedded_third_party_definitions"]),3)
    def test_gate(self): self.assertFalse(self.report["production"]["production_routed"])

if __name__=="__main__": unittest.main()
