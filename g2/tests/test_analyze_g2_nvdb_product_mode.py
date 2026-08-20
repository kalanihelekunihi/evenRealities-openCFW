import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_nvdb_product_mode.py';s=importlib.util.spec_from_file_location('pm',P);m=importlib.util.module_from_spec(s);sys.modules['pm']=m;s.loader.exec_module(m)
class NvdbProductModeAuditTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):c.r=m.analyze()
 def test_surface(c):c.assertEqual(c.r['surface'],{'linked_functions':6,'body_bytes':270,'physical_bytes':312,'direct_bl_ingress_sites':54,'direct_provider_calls':18,'stored_entry_pointers':[(0x6D1E94,0x4ABD91),(0x78F520,0x4ABDA5)],'strict_interior_ingress':0})
 def test_record(c):c.assertEqual(c.r['record'],{'address':0x200038F0,'boot_hex':'01000000','initialized_crc16':0x2E3E,'key':'nvProdMode'});c.assertFalse(c.r['behavior']['v1_crc_mismatch_rewrites_defaults']);c.assertTrue(c.r['behavior']['read_imports_record_without_validation'])
 def test_production_routed(c):
  p=c.r['production'];c.assertTrue(p['production_routed']);c.assertEqual(p['ownership_bytes'],270);c.assertEqual(p['retained_stock_noncode_bytes'],42);c.assertEqual(p['toolchain_profiles'],['apple-clang'])
  c.assertEqual(p['relocated_leaves'],['open_cfw_nvdb_product_mode_default_crc_initialize','open_cfw_nvdb_product_mode_get','open_cfw_nvdb_product_mode_load_and_migrate','open_cfw_nvdb_product_mode_read','open_cfw_nvdb_product_mode_set','open_cfw_nvdb_product_mode_update'])
  c.assertEqual(p['patch_sites'],['replace_nvdb_product_mode_default_crc_initialize','replace_nvdb_product_mode_get','replace_nvdb_product_mode_load_and_migrate','replace_nvdb_product_mode_read','replace_nvdb_product_mode_set','replace_nvdb_product_mode_update'])
if __name__=='__main__':unittest.main()
