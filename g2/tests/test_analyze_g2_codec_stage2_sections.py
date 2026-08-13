import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CodecStage2SectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("codec_stage2_sections",ROOT/"tools/analyze_g2_codec_stage2_sections.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_image_a_stage2_split(self):
  s=self.r["image_a"]["stage2"]
  self.assertEqual((s["xip_text"]["flash"],s["xip_text"]["size"]),("[0x3004, 0xBE88)",0x8E84))
  self.assertEqual((s["sram_text"]["iram"],s["sram_text"]["size"]),("[0x10023400, 0x100264E4)",0x30E4))
  self.assertEqual((s["sram_data"]["iram"],s["sram_data"]["size"]),("[0x100264E8, 0x10026D7C)",0x894))
  self.assertEqual(s["combined_sram_copy"]["size"],0x397C)
 def test_image_a_app(self):
  a=self.r["image_a"]["app"]
  self.assertEqual(a["iram_base"],"0x10023400");self.assertEqual(a["entry"],"0x10023500")
  self.assertEqual(a["handlers"],["0x10023640","0x10025574"])
  self.assertEqual(a["stack_pointer"],"0x2002f7fc")
  self.assertEqual(a["npu_sram_size_implied"],0x23400)
 def test_image_b(self):
  s=self.r["image_b"]["stage2"];a=self.r["image_b"]["app"]
  self.assertEqual(s["combined_sram_copy"]["iram"],"[0x10003000, 0x1001708C)")
  self.assertEqual((a["iram_base"],a["entry"],a["stack_pointer"]),("0x10003000","0x10003100","0x2002fffc"))
  self.assertEqual(a["handlers"],["0x10003240","0x10004880"])
 def test_kws_payload_offsets(self):
  k=self.r["kws_model_payload"]
  self.assertEqual((k["cmd"]["flash"],k["cmd"]["size"]),("[0xF804, 0x11BD0)",9164))
  self.assertEqual((k["weight"]["flash"],k["weight"]["size"]),("[0x11BD0, 0x2F3B0)",120800))
  self.assertIn("0x2F3B0",k["exact_fit"])
 def test_decoder_provenance(self):
  self.assertEqual(self.r["decoder"]["commit"],"2409f5af709d5fef4f41cbeb30ef59bc1046b252")
 def test_proprietary_boundary(self):
  self.assertFalse(self.r["production"]["production_routed"])
  self.assertIn("proprietary",self.r["production"]["ownership"])
 def test_fail_closed_on_blob_change(self):
  orig=self.m.CODEC
  class Fake:
   @staticmethod
   def read_bytes():return b"\x00"*326092
  self.m.CODEC=Fake
  try:self.assertRaises(self.m.AuditError,self.m.analyze)
  finally:self.m.CODEC=orig
 def test_fail_closed_on_manifest_change(self):
  orig=self.m.MANIFEST
  class Fake:
   @staticmethod
   def exists():return True
   @staticmethod
   def open(**kw):
    import io
    return io.StringIO("region\tsegment_offset\tsize\tsha256\tload_address\tentry\tevidence\n")
  self.m.MANIFEST=Fake
  try:self.assertRaises(self.m.AuditError,self.m.analyze)
  finally:self.m.MANIFEST=orig
if __name__=="__main__":unittest.main()
