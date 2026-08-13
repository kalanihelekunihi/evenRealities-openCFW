import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/"tools/analyze_g2_onboarding_controller.py"
S=importlib.util.spec_from_file_location("g2_onboarding_controller",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2OnboardingControllerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.report=M.analyze()
 def test_complete_object_and_restored_callbacks(self):
  s=self.report["surface"]
  self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"],s["baseline_path_anchored_functions"],s["path_anchored_functions"],s["body_bytes"],s["physical_bytes"],s["noncode_bytes"],s["reachable_instructions"]),(12,9,3,4,7,4136,4476,340,1558))
  self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"],s["indirect_body_calls"],s["direct_bl_entry_sites"],s["stored_entry_pointers"],s["strict_interior_ingress"]),(263,10,253,0,17,4,0))
 def test_state_and_callback_contract(self):
  b=self.report["behavior"]
  self.assertEqual(b["distinct_stored_callback_targets"],3)
  self.assertEqual((b["process_record_address"],b["ble_resume_record_address"]),("0x200F4800","0x200F47C4"))
  self.assertTrue(b["common_data_protobuf_dispatch"] and b["ble_disconnect_state_save"] and b["ble_reconnect_state_restore"])
  self.assertTrue(b["ui_init_registers_ble_callback"] and b["ui_exit_unregisters_ble_callback"])
 def test_all_reusable_edges_are_admitted(self):
  p=self.report["provider_boundary"]
  self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["cmsis_freertos_calls"],p["iar_memset_calls"],p["closed_onboarding_data_manager_calls"],p["closed_onboarding_kvdb_calls"],p["closed_onboarding_protobuf_calls"],p["closed_ble_callback_facade_calls"],p["first_party_policy_calls"]),(165,32,1,2,5,4,1,2,41))
  self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[])
  self.assertFalse(p["new_version_discriminator"] or p["private_generating_commit_recoverable"])
 def test_not_production_routed(self): self.assertFalse(self.report["production"]["production_routed"])
if __name__=="__main__": unittest.main()
