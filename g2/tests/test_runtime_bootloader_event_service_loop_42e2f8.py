import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_service_loop_42e2f8.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000;A=0x42E2F8;Z=0x42E39A;FN="open_cfw_bootloader_event_service_loop_42e2f8"
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));RS=((0x06,"open_cfw_bootloader_event_flags_init_42e254",0x42E254),(0x0A,"open_cfw_bootloader_noop_callback_42e276",0x42E276),(0x0E,"open_cfw_bootloader_event_runtime_setup_42e278",0x42E278),(0x12,"open_cfw_bootloader_event_wait_one_wrapper_42e2ea",0x42E2EA),(0x16,"open_cfw_bootloader_retained_state_probe_42e224",0x42E224),(0x2E,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x38,"open_cfw_bootloader_memset_wrapper_426c10",0x426C10),(0x42,"open_cfw_bootloader_runtime_context_create_42dca2",0x42DCA2),(0x58,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x62,"open_cfw_bootloader_memset_wrapper_426c10",0x426C10),(0x6C,"open_cfw_bootloader_runtime_context_create_42dca2",0x42DCA2),(0x74,"open_cfw_bootloader_noop_callback_42e39a",0x42E39A),(0x84,"open_cfw_bootloader_event_wait_4162c4",0x4162C4),(0x8A,"open_cfw_bootloader_runtime_time_4160e8",0x4160E8));VOID=ctypes.CFUNCTYPE(None)
class EventServiceLoopTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"loop.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.context=d.open_cfw_bootloader_event_service_context_42e2f8_portable;cls.context.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];cls.context.restype=ctypes.c_uint32;cls.step=d.open_cfw_bootloader_event_service_step_42e2f8_portable;cls.step.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,VOID];cls.step.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_context_paths(self):
  for state,line,first in ((0,0xD8,0),(7,0xD1,1)):
   context=(ctypes.c_uint32*10)(*([0xffffffff]*10));self.assertEqual(self.context(state,context),line);self.assertEqual(list(context),[first]+[0]*9)
 def test_bounded_wait_step(self):
  calls=[]
  @VOID
  def callback():calls.append(1)
  self.assertEqual(self.step(1,100,0,callback),0);self.assertEqual(calls,[1]);calls.clear();self.assertEqual(self.step(0x80000000,60000,0,callback),60000);self.assertEqual(calls,[]);self.assertEqual(self.step(0,0xffffffff,0xfffffff0,callback),0xfffffff0)
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes();rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in RS]
  with tempfile.TemporaryDirectory() as temp:
   for profile,cc in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True);body,_=apollo_overlay.extract_in_place_function_section(obj,FN,runtime_address=A,relocation_configs=rr,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[A-BASE:Z-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
