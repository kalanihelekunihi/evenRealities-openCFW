import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_control_orchestration_42dd14.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));ITEMS=(("open_cfw_bootloader_control_orchestrator_42dd14",0x42DD14,0x42DD68,((0x02,"open_cfw_bootloader_control_one_wrapper_42dd9a",0x42DD9A),(0x06,"open_cfw_bootloader_runtime_queue_context_init_42dd70",0x42DD70),(0x0A,"open_cfw_bootloader_runtime_context_wrapper_42dd68",0x42DD68),(0x0E,"open_cfw_bootloader_noop_callback_42dd98",0x42DD98),(0x12,"open_cfw_bootloader_control_two_wrapper_42dda4",0x42DDA4),(0x18,"open_cfw_bootloader_control_bits_dispatch_42e1c4",0x42E1C4),(0x26,"open_cfw_bootloader_event_wait_4162c4",0x4162C4),(0x4E,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_critical_dispatch_transaction_42de0e",0x42DE0E,0x42DE58,((0x16,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x1C,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x28,"open_cfw_bootloader_memcpy_words_4156ac",0x4156AC),(0x34,"open_cfw_bootloader_alignment_dispatch_42e4f4",0x42E4F4),(0x42,"open_cfw_bootloader_terminal_mode_42e514",0x42E514))));DISPATCH=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32,ctypes.c_uint32)
class ControlOrchestrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"orch.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.step=d.open_cfw_bootloader_control_orchestrator_step_42dd14_portable;cls.step.argtypes=[ctypes.c_uint32];cls.step.restype=ctypes.c_uint32;cls.transaction=d.open_cfw_bootloader_critical_dispatch_transaction_42de0e_portable;cls.transaction.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32,ctypes.c_uint32,DISPATCH];cls.transaction.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_wait_status_dispatch(self):
  self.assertEqual(self.step(0),0);self.assertEqual(self.step(1),1);self.assertEqual(self.step(0x7fffffff),1);self.assertEqual(self.step(0x80000000),0)
 def test_critical_transaction_copy(self):
  source=(ctypes.c_uint32*4)(1,2,3,4);copy=(ctypes.c_uint32*4)();calls=[]
  @DISPATCH
  def dispatch(words,h,c):calls.append((list(words[:4]),h,c));return 9
  self.assertEqual(self.transaction(source,copy,7,8,dispatch),9);self.assertEqual(list(copy),[1,2,3,4]);self.assertEqual(calls,[([1,2,3,4],7,8)])
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
