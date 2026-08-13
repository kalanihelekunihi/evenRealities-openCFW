import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/"tools/analyze_g2_silent_mode.py";S=importlib.util.spec_from_file_location("g2_silent_mode",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2SilentModeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_surface(self):
  s=self.r["surface"];self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"],s["body_bytes"],s["physical_bytes"],s["reachable_instructions"],s["direct_body_calls"],s["stored_entry_pointers"]),(10,7,3,2488,2696,957,178,3))
 def test_protocol(self):
  b=self.r["behavior"];self.assertEqual((b["common_data_record_id"],b["common_data_payload_bytes"],b["settings_status_offset"]),(0x10a,1,0x15));self.assertTrue(b["local_long_press_toggle"] and b["role_sensitive_remote_transition"])
 def test_providers(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["freertos_vtaskdelay_calls"],p["iar_memset_calls"],p["first_party_calls"],p["direct_cmsis_freertos_calls"]),(70,70,1,1,26,0));self.assertEqual(self.r["identity"]["embedded_third_party_definitions"],[])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
