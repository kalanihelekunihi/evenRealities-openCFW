import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ui_quicklist_page as q

class G2UIQuicklistPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=q.analyze()
    def test_complete_object(self):
        s=self.report['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_non_anchor_functions'],s['body_bytes'],s['physical_bytes']),(80,63,17,21886,23594))
        self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(1144,154,990))
    def test_ingress(self):
        s=self.report['surface'];self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_pointers'],s['strict_interior_ingress'],s['indirect_body_calls']),(164,15,0,0))
    def test_provider_boundary(self):
        p=self.report['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['iar_runtime_calls'],p['first_party_calls']),(415,465,5,24,81));self.assertFalse(p['new_version_discriminator'])
    def test_not_routed_or_third_party_body(self):
        self.assertFalse(self.report['production']['production_routed']);self.assertEqual(self.report['identity']['embedded_third_party_definitions'],[])

if __name__=='__main__':unittest.main()
