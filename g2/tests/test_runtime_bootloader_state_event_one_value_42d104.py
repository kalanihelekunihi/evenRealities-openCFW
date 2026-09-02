import ctypes,hashlib,importlib.util,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_state_event_one_value_42d104.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42D104;Z=0x42D3BC;BASE=0x410000;MAIN_BASE=0x437FE0;MAIN_A=0x5A0328;FN="open_cfw_bootloader_state_event_one_value_42d104";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
spec=importlib.util.spec_from_file_location("state_one_integrator",ROOT/"tools/integrate_g2_bootloader_state_event_one_value_42d104.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in mod.RS];FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
class Model(ctypes.Structure):_fields_=[(x,ctypes.c_uint32)for x in("mode_register","control80","control88","power380","tune344","tune34c","tune358","tune354","adjust4c","adjust44","control1b0","saved_nonactive_field4","saved_nonactive_low6","saved_active_field4")]+[("adjust_enabled",ctypes.c_uint8),("low6_clear",ctypes.c_uint8),("delay_calls",ctypes.c_uint32),("delay_total",ctypes.c_uint32)]
def field(v,n,w):return(v>>n)&((1<<w)-1)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"state.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.step=d.open_cfw_bootloader_state_event_one_value_42d104_portable;cls.step.argtypes=[ctypes.POINTER(Model),ctypes.c_uint32];cls.step.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_nonactive_save_saturate_and_delay(self):
  m=Model(mode_register=0,control80=0x3C00,control88=0xBFFFFFFC);self.assertEqual(self.step(ctypes.byref(m),1),0);self.assertEqual((m.saved_nonactive_field4,field(m.control80,10,4),m.saved_nonactive_low6,field(m.control88,0,6),m.delay_calls,m.delay_total),(15,2,60,63,1,15))
 def test_active_adjusted_profiles_and_saturation(self):
  for profile,expected in ((1,(10,8,16,20)),(2,(10,8,20,22))):
   m=Model(mode_register=3<<4,control80=(7<<10)|0x3FA,control88=0xFFFFFFFF,adjust4c=120,adjust44=125,adjust_enabled=1,low6_clear=1);self.assertEqual(self.step(ctypes.byref(m),profile),0);self.assertEqual((m.saved_active_field4,m.control80&0x3ff,field(m.control80,10,4)),(7,0x3FA,1));self.assertEqual((field(m.adjust4c,0,7),field(m.adjust44,0,7),m.control1b0&0x100),(127,127,0x100));self.assertEqual((field(m.tune344,25,5),field(m.tune34c,25,5),field(m.tune358,8,5),field(m.tune354,17,5)),expected);self.assertEqual((m.power380&0xF0000000,field(m.control88,0,6),m.delay_calls,m.delay_total),(0,0,2,15))
 def test_active_default_profile(self):
  m=Model(mode_register=3<<4,control80=0x123,control88=0xABCDEF00,adjust_enabled=0,low6_clear=0);self.assertEqual(self.step(ctypes.byref(m),9),0);self.assertEqual((m.control80&0x3ff,field(m.control88,0,6)),(0x123,1));self.assertEqual((field(m.tune344,11,5),field(m.tune34c,11,5),field(m.tune358,8,5),field(m.tune354,17,5)),(6,5,13,19))
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),mod.BH);analogue=MAIN.read_bytes()[MAIN_A-MAIN_BASE:MAIN_A-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),684)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual((r["relocation_count"],r["unrelocated_sha256"]),(3,mod.UH))
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
