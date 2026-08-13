#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/'tools/analyze_g2_app_ble_discovery.py'
class AppBleDiscoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('g2_app_ble_discovery',ANALYZER);assert s and s.loader
  cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closed_object(self):
  r=self.m.analyze();self.assertEqual(r['surface']['linked_functions'],2);self.assertEqual(r['surface']['body_bytes'],2962);self.assertEqual(r['surface']['physical_bytes'],3724);self.assertEqual(r['surface']['stored_entry_pointers'],3);self.assertEqual(r['identity']['ownership'],'g2_local_cordio_discovery_policy');self.assertIsNone(r['identity']['third_party_dependency']);self.assertEqual(r['behavior']['states'],list(range(9)));self.assertFalse(r['production']['production_routed'])
if __name__=='__main__':unittest.main()
