import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_register_profile_restore_42f2fa.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42F2FA;Z=0x42F38E;BASE=0x410000;FN="open_cfw_bootloader_hw_register_profile_restore_42f2fa";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x3C,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0x84,"open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8),(0x8C,"open_cfw_bootloader_mode_finalize_41cde0",0x41CDE0));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[(n,ctypes.c_uint32)for n in("mode_status","active","register_a","saved_a","register_b","saved_b","register_c","saved_c","register_d","saved_d","register_e","saved_e","power_toggles","finalize_calls")]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"r.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.restore=d.open_cfw_bootloader_hw_register_profile_restore_42f2fa_portable;cls.restore.argtypes=[ctypes.POINTER(Model)];cls.restore.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_non_mode_three_restores_two_fields(self):
  s=Model();s.register_a=s.register_b=0xffffffff;s.saved_a=0x15;s.saved_b=5;self.assertEqual(self.restore(ctypes.byref(s)),0);self.assertEqual(s.register_a&0x3f,0x15);self.assertEqual((s.register_b>>10)&0xf,5);self.assertEqual(s.finalize_calls,1)
 def test_mode_three_inactive_only_finalizes(self):
  s=Model();s.mode_status=3<<4;self.restore(ctypes.byref(s));self.assertEqual((s.power_toggles,s.finalize_calls),(0,1))
 def test_mode_three_active_restores_and_toggles(self):
  s=Model();s.mode_status=3<<4;s.active=1;s.register_c=s.register_d=s.register_e=0xffffffff;s.saved_c=2;s.saved_d=0x22;s.saved_e=9;self.restore(ctypes.byref(s));self.assertEqual((s.power_toggles,s.finalize_calls),(2,1));self.assertEqual((s.register_c>>29)&3,2);self.assertEqual(s.register_d&0x7f,0x22);self.assertEqual(s.register_e&0x100,0)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"b1b11b9cae5d09e8bd59aae4099ed288cbd5d1e55980dbdda910c89282b7af40")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],3)
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
