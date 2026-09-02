import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_orphan_services_430aec.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));CALL=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p)
ITEMS=(("open_cfw_bootloader_mode_four_wrapper_430aec",0x430AEC,32,"8b4d130ac1735011011fd8a65ded46b1c5892049315798e9c477e1745d031fb7",0x5A4F80,[{"offset":8,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mode_provider_430a60","symbol_type":"STT_NOTYPE","target_address":0x430A60}]),("open_cfw_bootloader_zero_table_431e38",0x431E38,56,"8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67",0x5FA01E,[]))
class TestOrphans(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"x.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True);dll=ctypes.CDLL(str(lib));cls.mode=dll.open_cfw_bootloader_mode_four_wrapper_430aec_portable;cls.mode.argtypes=[ctypes.c_uint32,CALL,ctypes.c_void_p];cls.mode.restype=ctypes.c_uint32;cls.zero=dll.open_cfw_bootloader_zero_table_431e38_portable;cls.zero.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32,ctypes.c_uint32];cls.zero.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_semantics(self):
  seen=[]
  @CALL
  def provider(h,m,c):seen.append((h,m));return 1
  self.assertEqual(self.mode(9,provider,None),0);self.assertEqual(seen,[(9,4)])
  memory=(ctypes.c_uint8*32)(*([0xAA]*32));table=(ctypes.c_uint32*5)(6,4,5,14,0)
  self.assertEqual(self.zero(table,memory,32,0),0);self.assertEqual(list(memory[4:10]),[0]*6);self.assertEqual(list(memory[14:19]),[0]*5)
  relative=(ctypes.c_uint32*3)(4,5,0);self.assertEqual(self.zero(relative,memory,32,8),0);self.assertEqual(list(memory[12:16]),[0]*4)
  bad=(ctypes.c_uint32*3)(8,30,0);self.assertEqual(self.zero(bad,memory,32,0),1)
 def test_exact(self):
  b=BOOT.read_bytes();m=MAIN.read_bytes()
  with tempfile.TemporaryDirectory() as d:
   for cc in PROFILES:
    obj=Path(d)/(cc.name+".o");subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True)
    for fn,s,z,h,ms,rel in ITEMS:
     stock=b[s-0x410000:s-0x410000+z];analogue=m[ms-0x437fe0:ms-0x437fe0+z];self.assertEqual(hashlib.sha256(stock).hexdigest(),h);self.assertEqual(stock,analogue);linked,report=apollo_overlay.extract_in_place_function_section(obj,fn,runtime_address=s,relocation_configs=rel,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(linked,stock);self.assertEqual(report["relocation_count"],len(rel))
 def test_reviewable(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
