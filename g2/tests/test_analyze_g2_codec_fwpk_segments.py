import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CodecFwpkSegmentTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("codec_fwpk_segments",ROOT/"tools/analyze_g2_codec_fwpk_segments.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_fwpk_container(self):
  f=self.r["fwpk"]
  self.assertEqual(f["version"],"0x00000203");self.assertEqual(f["record_count"],2)
  t=[(r["type"],r["size"],r["offset"]) for r in f["records"]]
  self.assertEqual(t,[(1,38236,48),(2,287808,38284)])
 def test_boot_image_identity(self):
  b=self.r["boot_image"]
  self.assertEqual(b["chip_id"],"0x8002");self.assertEqual(b["chip_type"],1);self.assertEqual(b["chip_version"],1)
  self.assertEqual(b["stage2_baud_rate"],1500000);self.assertEqual(b["stage2_checksum_bytesum"],"0x0024d441")
 def test_boot_stage_destinations(self):
  b=self.r["boot_image"]
  self.assertEqual((b["stage1"]["load_address"],b["stage1"]["size"],b["stage1"]["reset_vector"]),("0x10000000",10240,"0x10000100"))
  self.assertEqual(b["stage1"]["vector_entries"],64)
  self.assertEqual(b["stage1"]["trap_vectors"],["0x10000130","0x10000134"])
  self.assertEqual((b["stage2"]["load_address"],b["stage2"]["size"],b["stage2"]["reset_vector"]),("0x10002800",27964,"0x10002900"))
  self.assertEqual(b["stage2"]["distinct_handlers"],["0x10002994","0x10003124"])
 def test_main_image_dual_firmware(self):
  m=self.r["main_image"]
  a,b=m["image_a"],m["image_b"]
  self.assertEqual((a["image_offset"],a["stage2_size"],a["stage2_xip_text_size"]),(0,0xC800,0x8E84))
  self.assertEqual(a["stage1_block_crc32_mpeg2"],"0x21c58edb")
  self.assertEqual(a["stage2_offset"],0x3004);self.assertEqual(a["stage2_end"],0xF804)
  self.assertEqual((b["image_offset"],b["stage2_size"],b["stage2_xip_text_size"]),(0x2F3B0,0x1408C,0))
  self.assertEqual(b["stage1_block_crc32_mpeg2"],"0xa582510c")
  self.assertEqual(b["stage2_end"],287808)
  self.assertEqual(m["a_extra_payload"]["size"],129964)
 def test_segment_destinations(self):
  d=self.r["segment_destinations"]
  self.assertTrue(d["type1_boot_image"]["volatile"])
  self.assertEqual(d["type1_boot_image"]["stage2"]["load"],"0x10002800")
  self.assertFalse(d["type2_main_image"]["volatile"])
  self.assertEqual(d["type2_main_image"]["flash_offset"],0)
  self.assertEqual(d["type2_main_image"]["image_a"]["flash"],"[0x0, 0x2F3B0)")
  self.assertEqual(d["type2_main_image"]["image_b"]["flash"],"[0x2F3B0, 0x46440)")
 def test_flash_command(self):
  c=self.r["protocol"]["flash_command"]
  self.assertEqual(c["command_format"],"serialdown %d %d %d")
  self.assertEqual(c["flash_offset_argument"],0);self.assertEqual(c["chunk_argument"],0x2000)
  self.assertEqual(c["containing_object"],"service_codec_dfu.c")
 def test_community_source_profile_has_no_unresolved_codec_destination(self):
  p=self.r["community_source_profile"]
  self.assertEqual((p["regions"],p["placed_regions"],p["protocol_metadata_regions"],p["unresolved_regions"]),(6,4,2,0))
 def test_proprietary_boundary(self):
  self.assertFalse(self.r["production"]["production_routed"])
  self.assertIn("proprietary",self.r["production"]["codec_image_ownership"])
 def test_fail_closed_on_blob_change(self):
  orig=self.m.CODEC
  class Fake:
   @staticmethod
   def read_bytes():return b"\x00"*326092
  self.m.CODEC=Fake
  try:self.assertRaises(self.m.AuditError,self.m.analyze)
  finally:self.m.CODEC=orig
if __name__=="__main__":unittest.main()
