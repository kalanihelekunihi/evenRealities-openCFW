import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_small_services_42cea4.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_state_update_critical_42cea4",0x42CEA4,0x42CED8,((0x04,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x28,"open_cfw_bootloader_state_adjust_42cdf8",0x42CDF8))),("open_cfw_bootloader_chunked_indirect_visit_42d9f0",0x42D9F0,0x42DA1E,()),("open_cfw_bootloader_hardware_channel_normalize_42eda0",0x42EDA0,0x42EDF6,((0x46,"open_cfw_bootloader_clock_config_422364",0x422364),)),("open_cfw_bootloader_platform_boot_sequence_4301d6",0x4301D6,0x4301F4,((0x06,"open_cfw_bootloader_scb_priority_nibble_430280",0x430280),(0x0A,"open_cfw_bootloader_mode_one_apply_42fff2",0x42FFF2),(0x0E,"open_cfw_bootloader_platform_stage_430000",0x430000),(0x12,"open_cfw_bootloader_platform_prepare_41f612",0x41F612),(0x16,"open_cfw_bootloader_platform_finish_430502",0x430502))),("open_cfw_bootloader_address_validate_430a60",0x430A60,0x430A9C,((0x1A,"open_cfw_bootloader_address_limit_query_41d792",0x41D792),)))
BYTE=ctypes.CFUNCTYPE(None,ctypes.c_uint8);VISIT=ctypes.CFUNCTYPE(None,ctypes.c_uint32);PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32);VOID=ctypes.CFUNCTYPE(None)
class SmallServiceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"small.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.update=d.open_cfw_bootloader_state_update_critical_42cea4_portable;cls.update.argtypes=[ctypes.c_uint8,ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),BYTE];cls.visit=d.open_cfw_bootloader_chunked_indirect_visit_42d9f0_portable;cls.visit.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,VISIT];cls.visit.restype=ctypes.c_uint32;cls.normalize=d.open_cfw_bootloader_hardware_channel_normalize_42eda0_portable;cls.normalize.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),PAIR];cls.normalize.restype=ctypes.c_uint32;cls.validate=d.open_cfw_bootloader_address_validate_430a60_portable;cls.validate.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32];cls.validate.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_state_and_chunk_models(self):
  seen=[]
  @BYTE
  def adjust(v):seen.append(v)
  state=ctypes.c_uint8();pending=ctypes.c_uint8();self.update(7,0,ctypes.byref(state),ctypes.byref(pending),adjust);self.assertEqual((state.value,pending.value,seen),(7,0,[7]));self.update(9,1,ctypes.byref(state),ctypes.byref(pending),adjust);self.assertEqual((state.value,pending.value,seen),(9,1,[7]))
  visited=[]
  @VISIT
  def visit(v):visited.append(v)
  self.assertEqual(self.visit(0x1000,10,4,visit),3);self.assertEqual(visited,[0x1000,0x1004,0x1008])
 def test_hardware_model_and_address_validation(self):
  calls=[]
  @PAIR
  def clock(a,b):calls.append((a,b))
  handle=ctypes.c_uint32(0x02001234);control=ctypes.c_uint32(0x03000005);self.assertEqual(self.normalize(ctypes.byref(handle),0x1234,ctypes.byref(control),clock),0);self.assertEqual((handle.value,control.value,calls),(0x1234,0,[(4,15)]));self.assertEqual(self.validate(0x4000,9,10),1);self.assertEqual(self.validate(0x3fff,9,10),0);self.assertEqual(self.validate(0x4000,10,10),0)
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,cc in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for fn,a,z,specs in ITEMS:
     rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in specs];body,_=apollo_overlay.extract_in_place_function_section(obj,fn,runtime_address=a,relocation_configs=rr,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[a-BASE:z-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
