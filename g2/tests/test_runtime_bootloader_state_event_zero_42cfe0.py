import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_state_event_zero_42cfe0.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42CFE0;Z=0x42D0F2;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_state_event_zero_42cfe0";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));RELOCS=[{"offset":0x22,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_probe_41f3f0","symbol_type":"STT_NOTYPE","target_address":0x41F3F0}]
class Model(ctypes.Structure):_fields_=[("enabled",ctypes.c_uint8),("mode",ctypes.c_uint8),("probe_status",ctypes.c_uint32),("state_word",ctypes.c_uint32),("bitmap",ctypes.c_uint32),("channel",ctypes.c_uint32*16),("output",ctypes.c_uint8)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"zero.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.classify=d.open_cfw_bootloader_state_event_zero_42cfe0_portable;cls.classify.argtypes=[ctypes.POINTER(Model)]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_disabled_is_noop_and_mode_two_sets_output(self):
  s=Model();s.output=7;self.classify(ctypes.byref(s));self.assertEqual(s.output,7);s.enabled=1;s.mode=2;self.classify(ctypes.byref(s));self.assertEqual(s.output,1)
 def test_probe_state_shortcut(self):
  for value,expected in ((0,0),(1,1),(2,1),(3,0),(15,0)):
   s=Model();s.enabled=1;s.probe_status=1;s.state_word=value;s.output=9;self.classify(ctypes.byref(s));self.assertEqual(s.output,expected)
 def classify_value(self,value,reg_enabled=1,bitmap_enabled=1):
  s=Model();s.enabled=1;s.bitmap=bitmap_enabled;s.channel[0]=(value<<8)|reg_enabled;s.output=9;self.classify(ctypes.byref(s));return s.output
 def test_channel_range_boundaries(self):
  for value,expected in ((0,1),(5,1),(6,0),(18,0),(19,1),(24,1),(25,0),(255,0),(256,1),(479,1),(480,0),(511,0)):self.assertEqual(self.classify_value(value),expected,value)
 def test_channel_requires_register_and_bitmap_enable(self):self.assertEqual(self.classify_value(0,0,1),0);self.assertEqual(self.classify_value(0,1,0),0)
 def test_invalid_model_is_safe(self):self.classify(None)
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"c03a0f379d7bbafb93e2c9074e4d754081699d39c63b4c2820765ffdab996624");analogue=MAIN.read_bytes()[0x5A0204-MAIN_BASE:0x5A0204-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),271)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],1);self.assertEqual(r["unrelocated_sha256"],"01821e038de30d1a7e3cf1f0cb4e6124781b6860f1931800f3e89fe167b00e6a")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
