import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_state_register_initialize_42d3bc.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42D3BC;Z=0x42D562;BASE=0x410000;MB=0x437FE0;MA=0x5A05E0;FN="open_cfw_bootloader_state_register_initialize_42d3bc";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x7C,"open_cfw_bootloader_delay_us_41d1c0",0x41D1C0),(0xA6,"open_cfw_bootloader_delay_us_41d1c0",0x41D1C0));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("mode_register",ctypes.c_uint32),("control80",ctypes.c_uint32),("control88",ctypes.c_uint32),("power380",ctypes.c_uint32),("tune344",ctypes.c_uint32),("tune34c",ctypes.c_uint32),("tune358",ctypes.c_uint32),("tune354",ctypes.c_uint32),("adjust4c",ctypes.c_uint32),("adjust44",ctypes.c_uint32),("control1b0",ctypes.c_uint32),("saved_low6",ctypes.c_uint32),("saved_field4",ctypes.c_uint32),("saved_restore4",ctypes.c_uint32),("adjust_enabled",ctypes.c_uint8),("low6_clear",ctypes.c_uint8),("delay_calls",ctypes.c_uint32),("delay_total",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"state.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.apply=d.open_cfw_bootloader_state_register_initialize_42d3bc_portable;cls.apply.argtypes=[ctypes.POINTER(Model)];cls.apply.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_nonactive_restore(self):
  m=Model(saved_low6=0x2a,saved_field4=9);self.assertEqual(self.apply(ctypes.byref(m)),0);self.assertEqual((m.control88&63,(m.control80>>10)&15),(0x2a,9))
 def test_active_program_cleanup_and_delays(self):
  m=Model(mode_register=3<<4,control80=100,control88=0xffffffff,power380=7,control1b0=0xffffffff);self.assertEqual(self.apply(ctypes.byref(m)),0);self.assertEqual((m.control80&0x3ff,m.control88&63,m.power380>>28,m.delay_calls,m.delay_total),(100,1,0,2,15));self.assertEqual(((m.tune344>>25)&31,(m.tune344>>11)&31,(m.tune34c>>25)&31,(m.tune358>>8)&31,(m.tune354>>17)&31),(6,6,5,7,10))
 def test_adjustments_and_saturation(self):
  m=Model(mode_register=3<<4,control80=0x3fe,adjust_enabled=1,adjust4c=16,adjust44=9,saved_restore4=11,control1b0=0x100,low6_clear=1);self.assertEqual(self.apply(ctypes.byref(m)),0);self.assertEqual((m.adjust4c&127,m.adjust44&127,(m.control80>>10)&15,m.control1b0&0x100,m.control88&63),(1,0,11,0,0))
 def test_invalid_model(self):self.assertEqual(self.apply(None),0xffffffff)
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"28b119628520d11368f8517e23ba59254c17bb974684a59ead1266312f71e0c6");analogue=MAIN.read_bytes()[MA-MB:MA-MB+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),414)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],2);self.assertEqual(r["unrelocated_sha256"],"e9f07abd3d46704129114ec4e23d3a0702e9fab7d84c19b1b3376ea27e06af46")
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
