#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/'tools/analyze_g2_app_ble_peer_manager.py'
class AppBlePeerManagerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('g2_app_ble_peer_manager',ANALYZER);assert s and s.loader
  cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closed_object(self):
  r=self.m.analyze();self.assertEqual(r['surface']['linked_functions'],4);self.assertEqual(r['surface']['additional_recovered_functions'],2);self.assertEqual(r['surface']['physical_bytes'],512);self.assertEqual(r['identity']['ownership'],'g2_local_cordio_application_adapter');self.assertIsNone(r['identity']['third_party_dependency']);self.assertTrue(r['behavior']['connected_or_opening_path_closes_before_deferred_unpair'])
  p=r['production'];self.assertTrue(p['production_routed']);self.assertEqual(p['ownership_bytes'],446);self.assertEqual(p['source_functions'],4);self.assertEqual(p['compiled_text_bytes'],{'apple-clang':326,'linux-clang':326});self.assertEqual(p['strict_relocations'],17);self.assertFalse(p['software_functional_gap']);self.assertEqual(p['hardware_validation'],'blocked by unavailable physical evidence');self.assertEqual(p['hardware_operations'],[]);self.assertEqual(len(p['hardware_evidence_required']),2)
if __name__=='__main__':unittest.main()
