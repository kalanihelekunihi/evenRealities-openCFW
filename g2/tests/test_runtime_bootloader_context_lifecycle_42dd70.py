import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_context_lifecycle_42dd70.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_runtime_queue_context_init_42dd70",0x42DD70,0x42DD98,((0x0C,"open_cfw_bootloader_runtime_queue_create_416816",0x416816),(0x18,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),("open_cfw_bootloader_runtime_action_context_init_42ddae",0x42DDAE,0x42DDDA,((0x10,"open_cfw_bootloader_runtime_dispatch_4160fe",0x4160FE),(0x1C,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),("open_cfw_bootloader_runtime_action_context_deinit_42ddda",0x42DDDA,0x42DDF2,((0x0E,"open_cfw_bootloader_runtime_action_416200",0x416200),)),("open_cfw_bootloader_runtime_enable_sequence_42ddf2",0x42DDF2,0x42DE0E,((0x02,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x08,"open_cfw_bootloader_runtime_enable_41f8ba",0x41F8BA),(0x12,"open_cfw_bootloader_runtime_mode_set_41ba80",0x41BA80),(0x16,"open_cfw_bootloader_runtime_commit_41c990",0x41C990))))
CREATE=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32);DISPATCH=CREATE;ACTION=ctypes.CFUNCTYPE(None,ctypes.c_uint32);VOID=ctypes.CFUNCTYPE(None)
class ContextLifecycleTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"context.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.queue=d.open_cfw_bootloader_runtime_queue_context_init_42dd70_portable;cls.queue.argtypes=[ctypes.POINTER(ctypes.c_uint32),CREATE];cls.queue.restype=ctypes.c_uint32;cls.init=d.open_cfw_bootloader_runtime_action_context_init_42ddae_portable;cls.init.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32,ctypes.c_uint32,DISPATCH];cls.init.restype=ctypes.c_uint32;cls.deinit=d.open_cfw_bootloader_runtime_action_context_deinit_42ddda_portable;cls.deinit.argtypes=[ctypes.POINTER(ctypes.c_uint32),ACTION];cls.deinit.restype=ctypes.c_uint32;cls.sequence=d.open_cfw_bootloader_runtime_enable_sequence_42ddf2_portable;cls.sequence.argtypes=[VOID,ACTION,ACTION,VOID]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_init_and_failure_status(self):
  seen=[]
  @CREATE
  def create(a,b,c):seen.append((a,b,c));return 0x55
  slot=ctypes.c_uint32();self.assertEqual(self.queue(ctypes.byref(slot),create),1);self.assertEqual((slot.value,seen),(0x55,[(0x32,0x28,0)]))
  @DISPATCH
  def dispatch(a,b,c):seen.append((a,b,c));return 0
  self.assertEqual(self.init(ctypes.byref(slot),7,9,dispatch),0);self.assertEqual(slot.value,0)
 def test_deinit_and_sequence_order(self):
  seen=[]
  @ACTION
  def action(v):seen.append(v)
  slot=ctypes.c_uint32(0x44);self.assertEqual(self.deinit(ctypes.byref(slot),action),1);self.assertEqual((slot.value,seen),(0,[0x44]));self.assertEqual(self.deinit(ctypes.byref(slot),action),0)
  @VOID
  def enter():seen.append("enter")
  @VOID
  def commit():seen.append("commit")
  self.sequence(enter,action,action,commit);self.assertEqual(seen,[0x44,"enter",1,1,"commit"])
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
