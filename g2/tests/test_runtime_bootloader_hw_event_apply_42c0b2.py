import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_event_apply_42c0b2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42C0B2;Z=0x42C222;BASE=0x410000;FN="open_cfw_bootloader_hw_event_apply_42c0b2";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));RELOCS=[{"offset":0xC8,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_delay_cycles_41d1c0","symbol_type":"STT_NOTYPE","target_address":0x41D1C0}]
class Model(ctypes.Structure):_fields_=[(n,ctypes.c_uint32)for n in("instance","delay_unit","register_100","register_108","register_10c","register_110","register_11c","register_200","register_208","register_218","register_21c","status_248","register_388","drain_writes","delay_cycles")]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"a.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.apply=d.open_cfw_bootloader_hw_event_apply_42c0b2_portable;cls.apply.argtypes=[ctypes.POINTER(Model),ctypes.c_uint32]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def model(self):
  s=Model();s.delay_unit=7;s.register_110=0xffffffff;s.register_11c=0xffffffff;s.register_200=0x12345678;s.status_248=4;s.register_388=0x55;return s
 def test_null_and_terminal_restore(self):
  self.apply(None,0);s=self.model();self.apply(ctypes.byref(s),0);self.assertEqual((s.register_200,s.register_208),(0x12345678,0xffffffff))
 def test_drain_writes(self):
  s=self.model();s.register_218=2;s.register_21c=13;s.register_100=4<<8;self.apply(ctypes.byref(s),0x800);self.assertEqual((s.drain_writes,s.register_10c),(4,0x08000001))
 def test_timed_pulse_restores_register_and_sets_controls(self):
  s=self.model();self.apply(ctypes.byref(s),0x210);self.assertEqual((s.register_388,s.delay_cycles),(0x55,42));self.assertEqual(s.register_110&2,2);self.assertEqual(s.register_11c&0x10,0x10)
 def test_pulse_requires_ready_status(self):
  s=self.model();s.status_248=0;self.apply(ctypes.byref(s),0x210);self.assertEqual(s.delay_cycles,0)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"a3d5075b7f480a21b071c587bb343466ca39d411ed426927e82b22168591937e")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],1)
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
