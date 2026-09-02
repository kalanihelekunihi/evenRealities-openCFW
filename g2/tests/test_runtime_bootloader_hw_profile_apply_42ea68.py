import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_profile_apply_42ea68.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42EA68;Z=0x42EAF6;BASE=0x410000;FN="open_cfw_bootloader_hw_profile_apply_42ea68";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));RELOCS=[{"offset":0x2E,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mode_enable_route_4222f0","symbol_type":"STT_NOTYPE","target_address":0x4222F0}]
class Model(ctypes.Structure):_fields_=[("header",ctypes.c_uint32),("published",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"p.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.apply=d.open_cfw_bootloader_hw_profile_apply_42ea68_portable;cls.apply.argtypes=[ctypes.POINTER(Model),ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32];cls.apply.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_validation_and_route_status(self):
  p=(ctypes.c_uint8*7)(2,0,0,0,0,0,0);self.assertEqual(self.apply(None,p,0),2);s=Model(0x01AFAFAF,0);p[0]=1;self.assertEqual(self.apply(ctypes.byref(s),p,0),6);p[0]=2;self.assertEqual(self.apply(ctypes.byref(s),p,5),5)
 def test_field_pack(self):
  s=Model(0x01AFAFAF,0);p=(ctypes.c_uint8*7)(2,1,1,5,1,0,1);self.assertEqual(self.apply(ctypes.byref(s),p,0),0);self.assertEqual(s.published,0x021D1014)
 def test_masks_high_bits(self):
  s=Model(0x01AFAFAF,0);p=(ctypes.c_uint8*7)(2,3,2,15,4,3,2);self.assertEqual(self.apply(ctypes.byref(s),p,0),0);self.assertEqual(s.published&1,0)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"1e62bb87b3abb1f8918525f1f3064c366982fc0afa075a018925d8f21376d686")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],1)
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
