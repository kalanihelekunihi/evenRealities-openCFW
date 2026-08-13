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
  r=self.m.analyze();self.assertEqual(r['surface']['linked_functions'],4);self.assertEqual(r['surface']['additional_recovered_functions'],2);self.assertEqual(r['surface']['physical_bytes'],512);self.assertEqual(r['identity']['ownership'],'g2_local_cordio_application_adapter');self.assertIsNone(r['identity']['third_party_dependency']);self.assertTrue(r['behavior']['connected_or_opening_path_closes_before_deferred_unpair']);self.assertFalse(r['production']['production_routed'])
if __name__=='__main__':unittest.main()
