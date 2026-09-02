import ctypes, hashlib
from pathlib import Path
import shutil, subprocess, sys, tempfile, unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_state_range_dispatch_42cdf8.c"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE=0x00410000;MAIN_BASE=0x00437FE0
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES={"apple":ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang","linux":Path("/opt/homebrew/opt/llvm@22/bin/clang")}
APPLY=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_void_p)
EVENT=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p)
RANGE_CB=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_void_p,ctypes.c_void_p)
class Range(ctypes.Structure):_fields_=[("sample",ctypes.c_float),("lower",ctypes.c_float),("upper",ctypes.c_float)]

class StateRangeDispatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"state.so";cc=shutil.which("cc") or shutil.which("clang")
  subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
  cls.dll=ctypes.CDLL(str(lib));cls.adjust=cls.dll.open_cfw_bootloader_state_adjust_42cdf8_portable
  cls.adjust.argtypes=[ctypes.c_uint32,ctypes.c_uint8,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint8,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)]
  cls.update=cls.dll.open_cfw_bootloader_state_range_update_42ced8_portable
  cls.update.argtypes=[ctypes.POINTER(Range),ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint8),APPLY,ctypes.c_void_p];cls.update.restype=ctypes.c_uint32
  cls.dispatch=cls.dll.open_cfw_bootloader_state_event_dispatch_42d562_portable
  cls.dispatch.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint8),EVENT,EVENT,EVENT,RANGE_CB,ctypes.c_void_p];cls.dispatch.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_adjustment_gates_and_saturates(self):
  target=ctypes.c_uint32(0xA5000064);self.adjust(0,0,0x30,0,0,50,ctypes.byref(target));self.assertEqual(target.value,0xA5000064)
  self.adjust(0,1,0x30,0,0,50,ctypes.byref(target));self.assertEqual(target.value&127,40)
  self.adjust(2,1,0x30,1<<18,1,120,ctypes.byref(target));self.assertEqual(target.value&127,127)
 def test_range_boundaries_and_flags(self):
  calls=[]
  @APPLY
  def apply(value,_):calls.append(value)
  cases=((-273.0,0,-273.0,35.0),(34.999,0,-273.0,35.0),(35.0,1,33.0,50.0),(50.0,2,48.0,1000.0),(999.0,2,48.0,1000.0))
  for sample,kind,lower,upper in cases:
   state=Range(sample,0,0);flag=ctypes.c_uint8(9);self.assertEqual(self.update(ctypes.byref(state),0,ctypes.byref(flag),apply,None),0)
   self.assertEqual((state.lower,state.upper),(lower,upper));self.assertEqual(flag.value,1 if kind==2 else 0)
  for sample in (-274.0,1000.0,float("nan")):
   state=Range(sample,1,1);flag=ctypes.c_uint8(7);self.assertEqual(self.update(ctypes.byref(state),0,ctypes.byref(flag),apply,None),1);self.assertEqual((state.lower,state.upper),(0.0,0.0))
  self.assertEqual(calls,[0,0,1,2,2])
 def test_dispatch_routes(self):
  calls=[]
  def callback(tag,result):
   @EVENT
   def inner(value,_):calls.append((tag,value));return result
   return inner
  zero=callback("z",3);one0=callback("o0",4);onev=callback("ov",5)
  @RANGE_CB
  def rng(pointer,_):calls.append(("r",ctypes.cast(pointer,ctypes.POINTER(ctypes.c_uint8))[0]));return 6
  state=ctypes.c_uint8(2);self.assertEqual(self.dispatch(0,ctypes.byref(state),zero,one0,onev,rng,None),0)
  state.value=0;self.assertEqual(self.dispatch(1,ctypes.byref(state),zero,one0,onev,rng,None),4)
  state.value=7;self.assertEqual(self.dispatch(1,ctypes.byref(state),zero,one0,onev,rng,None),5)
  self.assertEqual(self.dispatch(2,ctypes.byref(state),zero,one0,onev,rng,None),6)
  self.assertEqual(self.dispatch(6,ctypes.byref(state),zero,one0,onev,rng,None),0)
  self.assertEqual(calls,[("z",2),("o0",0),("ov",7),("r",7)])
 def test_dual_toolchain_and_main_analogues(self):
  specs=[("open_cfw_bootloader_state_adjust_42cdf8",0x42CDF8,0x42CEA4,0x5A001C,[],frozenset()),
   ("open_cfw_bootloader_state_range_update_42ced8",0x42CED8,0x42CFE0,0x5A00FC,[{"offset":x,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_apply_42cea4","symbol_type":"STT_NOTYPE","target_address":0x42CEA4} for x in (0xA0,0xC8,0xEC)],frozenset()),
   ("open_cfw_bootloader_state_event_dispatch_42d562",0x42D562,0x42D5C2,0x5A0786,[{"offset":0x2A,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_event_zero_42cfe0","symbol_type":"STT_NOTYPE","target_address":0x42CFE0},{"offset":0x3A,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_event_one_zero_42d3bc","symbol_type":"STT_NOTYPE","target_address":0x42D3BC},{"offset":0x44,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_event_one_value_42d104","symbol_type":"STT_NOTYPE","target_address":0x42D104},{"offset":0x4E,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_state_range_update_42ced8","symbol_type":"STT_FUNC","target_address":0x42CED8}],frozenset({"open_cfw_bootloader_state_range_update_42ced8"}))]
  boot=BOOT.read_bytes();main=MAIN.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in PROFILES.items():
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,analogue,relocs,allowed in specs:
     body,report=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,allowed_defined_relocation_targets=allowed,strict_relocation_contract=True,allow_discarded_alloc_sections=True)
     stock=boot[start-BOOT_BASE:end-BOOT_BASE];self.assertEqual(body,stock,profile);self.assertEqual(stock,main[analogue-MAIN_BASE:analogue-MAIN_BASE+len(stock)])
 def test_source_is_reviewable(self):
  body=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",body)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,body)
if __name__=="__main__":unittest.main()
