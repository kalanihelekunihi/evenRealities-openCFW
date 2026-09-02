import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_value_profile_42f204.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42F204;Z=0x42F2FA;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_event_value_provider_42f204";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x0C,"open_cfw_bootloader_mode_finalize_41cde0",0x41CDE0),(0x64,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0xD0,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0xD6,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0),(0xEE,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):
 _fields_=[("status",ctypes.c_uint32),("control",ctypes.c_uint32),("trim",ctypes.c_uint32),("saved_control",ctypes.c_uint32),("saved_trim",ctypes.c_uint32),("active_allowed",ctypes.c_uint8),("source_first",ctypes.c_uint32),("target_first",ctypes.c_uint32),("feature_first",ctypes.c_uint32),("source_second",ctypes.c_uint32),("target_second",ctypes.c_uint32),("feature_second",ctypes.c_uint32),("finalize_calls",ctypes.c_uint32),("power_off_calls",ctypes.c_uint32),("power_on_calls",ctypes.c_uint32),("delay",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"profile.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.apply=d.open_cfw_bootloader_event_value_provider_42f204_portable;cls.apply.argtypes=[ctypes.c_uint32,ctypes.POINTER(Model)];cls.apply.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_saved_field_path_and_saturation(self):
  s=Model();s.status=0;s.control=0xA<<10;s.trim=0x1234003C;self.assertEqual(self.apply(1,ctypes.byref(s)),0);self.assertEqual(s.finalize_calls,1);self.assertEqual(s.saved_control,0xA);self.assertEqual((s.control>>10)&15,2);self.assertEqual(s.saved_trim,60);self.assertEqual(s.trim&63,63);self.assertEqual(s.delay,15)
  s=Model();s.control=7<<10;s.trim=12;self.apply(2,ctypes.byref(s));self.assertEqual((s.finalize_calls,s.saved_trim,s.trim&63),(0,12,17))
 def test_active_path_applies_all_fields(self):
  s=Model();s.status=3<<4;s.active_allowed=1;s.control=15<<10;s.source_first=120;s.target_first=0xFFFF0000;s.source_second=100;s.target_second=0xAAAA0080;self.assertEqual(self.apply(3,ctypes.byref(s)),0);self.assertEqual(s.finalize_calls,1);self.assertEqual((s.power_off_calls,s.power_on_calls,s.delay),(1,1,15));self.assertEqual((s.control>>10)&15,1);self.assertEqual(s.target_first&127,127);self.assertEqual(s.target_second&127,115);self.assertEqual(s.feature_first&0x100,0x100);self.assertEqual(s.feature_second&0x60000000,0x60000000)
 def test_active_path_respects_gate(self):
  s=Model();s.status=3<<4;s.active_allowed=0;self.apply(2,ctypes.byref(s));self.assertEqual((s.power_off_calls,s.power_on_calls,s.delay,s.finalize_calls),(0,0,0,0))
 def test_invalid_state(self):self.assertEqual(self.apply(0,None),0xFFFFFFFF)
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"501f73cf98677984aeedc3b9d60df3775a99c7e68520f23d6bd11c8b0e342317");analogue=MAIN.read_bytes()[0x59FBAC-MAIN_BASE:0x59FBAC-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),234)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],5);self.assertEqual(r["unrelocated_sha256"],"afc00b5ad826855d562f2c1f82f67b728ea5144b92754578cc319e35fcb10b0d")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
