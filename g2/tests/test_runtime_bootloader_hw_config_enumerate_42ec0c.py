import ctypes,hashlib,math
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_config_enumerate_42ec0c.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";BOOT_BASE=0x410000;MAIN_BASE=0x437FE0
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES={"apple":ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang","linux":Path("/opt/homebrew/opt/llvm@22/bin/clang")}
class Handle(ctypes.Structure):_fields_=[("word0",ctypes.c_uint32),("word1",ctypes.c_uint32)]
class Quad(ctypes.Structure):_fields_=[("word",ctypes.c_uint32*4)]
class Pair(ctypes.Structure):_fields_=[("value",ctypes.c_uint32),("channel",ctypes.c_uint32)]
class Model(ctypes.Structure):_fields_=[("limit0",ctypes.c_uint32),("limit1",ctypes.c_uint32),("selector",ctypes.c_uint32),("calibration",ctypes.c_float*4),("pair",ctypes.c_float*2),("accumulator",ctypes.c_float),("channels",ctypes.c_uint32*8),("traversal",ctypes.c_uint32),("normalize_enabled",ctypes.c_uint8)]
def fbits(value):return ctypes.cast(ctypes.pointer(ctypes.c_float(value)),ctypes.POINTER(ctypes.c_uint32))[0]
class HardwareConfigEnumerateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"hw.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib))
  cls.dispatch=dll.open_cfw_bootloader_hw_config_dispatch_42ec0c_portable;cls.dispatch.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(Quad),ctypes.POINTER(Model)];cls.dispatch.restype=ctypes.c_uint32
  cls.normalize=dll.open_cfw_bootloader_hw_channel_normalize_42ee00_portable;cls.normalize.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Model)];cls.normalize.restype=ctypes.c_uint32
  cls.enumerate=dll.open_cfw_bootloader_hw_channel_enumerate_42ee70_portable;cls.enumerate.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(Pair),ctypes.POINTER(Model)];cls.enumerate.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_dispatch_operations_and_errors(self):
  handle=Handle(0x01AFAFAF,0);model=Model();q=Quad((1,0x12345,0xABCDE,0));self.assertEqual(self.dispatch(ctypes.byref(handle),0,ctypes.byref(q),ctypes.byref(model)),0);self.assertEqual((model.limit0,model.limit1,model.selector),(0x12345,0xABCDE,1))
  q.word[:]=(fbits(2.0),0,0xC2F6E979,0);model.calibration[:]=(1.0,0.1,0.2,0.0);self.assertEqual(self.dispatch(ctypes.byref(handle),1,ctypes.byref(q),ctypes.byref(model)),0);self.assertNotEqual(q.word[1],0)
  q.word[:]=(0,0,0,0xC2F6E979);self.assertEqual(self.dispatch(ctypes.byref(handle),2,ctypes.byref(q),ctypes.byref(model)),0);self.assertEqual(q.word[0],fbits(1.0))
  q.word[:]=(0,0,0,0xC2F6E979);model.pair[:]=(3.0,4.0);self.assertEqual(self.dispatch(ctypes.byref(handle),3,ctypes.byref(q),ctypes.byref(model)),0);self.assertEqual(tuple(q.word),(fbits(3.0),fbits(4.0),0,0))
  bad=Handle(0,0);self.assertEqual(self.dispatch(ctypes.byref(bad),0,ctypes.byref(q),ctypes.byref(model)),2);self.assertEqual(self.dispatch(ctypes.byref(handle),9,ctypes.byref(q),ctypes.byref(model)),6)
 def test_normalize_gating_and_input_enumeration(self):
  model=Model();model.pair[:]=(0.0,0.0);value=(3<<28)|(2048<<6)|17;self.assertEqual(self.normalize(value,1,ctypes.byref(model)),value);model.normalize_enabled=1;normalized=self.normalize(value,1,ctypes.byref(model));self.assertEqual(normalized&0xFFF00000,value&0xFFF00000);self.assertEqual(normalized&63,0)
  for i in range(8):model.channels[i]=8<<8
  source=(ctypes.c_uint32*2)((2<<28)|(100<<6),(5<<28)|(200<<6));count=ctypes.c_uint32(2);out=(Pair*2)();handle=Handle(0x01AFAFAF,0);self.assertEqual(self.enumerate(ctypes.byref(handle),0,source,ctypes.byref(count),out,ctypes.byref(model)),0);self.assertEqual(count.value,2);self.assertEqual((out[0].channel,out[1].channel),(2,5))
 def test_dual_toolchain_and_main_analogues(self):
  specs=[("open_cfw_bootloader_hw_config_dispatch_42ec0c",0x42EC0C,0x42ED60,0x55DC88,[],frozenset()),("open_cfw_bootloader_hw_channel_normalize_42ee00",0x42EE00,0x42EE6C,0x55DE7C,[],frozenset()),("open_cfw_bootloader_hw_channel_enumerate_42ee70",0x42EE70,0x42EFF4,0x55DEEC,[{"offset":x,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_hw_channel_normalize_42ee00","symbol_type":"STT_FUNC","target_address":0x42EE00} for x in (0x5A,0x160)],frozenset({"open_cfw_bootloader_hw_channel_normalize_42ee00"}))];boot=BOOT.read_bytes();main=MAIN.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in PROFILES.items():
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,analogue,relocs,allowed in specs:
     body,report=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,allowed_defined_relocation_targets=allowed,strict_relocation_contract=True,allow_discarded_alloc_sections=True);stock=boot[start-BOOT_BASE:end-BOOT_BASE];self.assertEqual(body,stock,profile);self.assertEqual(stock,main[analogue-MAIN_BASE:analogue-MAIN_BASE+len(stock)])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
