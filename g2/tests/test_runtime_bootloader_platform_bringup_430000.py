import ctypes,hashlib,importlib.util,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_platform_bringup_430000.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x430000;Z=0x4301D6;BASE=0x410000;FN="open_cfw_bootloader_platform_bringup_430000";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
spec=importlib.util.spec_from_file_location("bringup_integrator",ROOT/"tools/integrate_g2_bootloader_platform_bringup_430000.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);SPECS=mod.RS;RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS];FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
class Model(ctypes.Structure):_fields_=[("init_status",ctypes.c_uint32),("enumerate_calls",ctypes.c_uint32),("capture_status",ctypes.c_uint32),("profile_status",ctypes.c_uint32),("channel_status",ctypes.c_uint32),("activate_status",ctypes.c_uint32),("sample_status",ctypes.c_uint32*3),("sample_raw",ctypes.c_uint32*3),("begin_calls",ctypes.c_uint32),("end_calls",ctypes.c_uint32),("restore_calls",ctypes.c_uint32),("reset_calls",ctypes.c_uint32),("teardown_calls",ctypes.c_uint32),("valid",ctypes.c_uint8),("category",ctypes.c_uint32),("value",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"bringup.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.bringup=d.open_cfw_bootloader_platform_bringup_430000_portable;cls.bringup.argtypes=[ctypes.POINTER(Model)];cls.bringup.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_measurement_attempts_range_and_teardown(self):
  m=Model();m.sample_status[0]=1;m.sample_raw[:]=(0,100,200);self.assertEqual(self.bringup(ctypes.byref(m)),0);self.assertEqual((m.enumerate_calls,m.begin_calls,m.end_calls,m.restore_calls,m.reset_calls,m.teardown_calls),(1,1,1,1,1,1));self.assertEqual(m.value,(0x4a6*200)>>12)
 def test_invalid(self):self.assertEqual(self.bringup(None),0xffffffff)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"c98f998d82e0cac0d01306057a759bbe3c360091397866e4e5999094a558879d")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],23);self.assertEqual(r["unrelocated_sha256"],"62f91d410489b31b78356faa7ae9764b0b335fac5d2571074b3678e51cf251f0")
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
