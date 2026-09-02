import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_runtime_services_42e53c.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));ITEMS=(("open_cfw_bootloader_event_runtime_init_42e53c",0x42E53C,0x42E642,((0x14,"open_cfw_bootloader_queue_create_416816",0x416816),(0x38,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x54,"open_cfw_bootloader_named_object_create_4163b2",0x4163B2),(0x78,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x8C,"open_cfw_bootloader_event_object_create_416610",0x416610),(0xB0,"open_cfw_bootloader_log_4176ce",0x4176CE),(0xC2,"open_cfw_bootloader_runtime_object_delete_416200",0x416200),(0xDA,"open_cfw_bootloader_runtime_task_create_4160fe",0x4160FE),(0xFE,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_event_callback_loop_42e644",0x42E644,0x42E686,((0x1A,"open_cfw_bootloader_queue_receive_416920",0x416920),(0x3C,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_event_callback_enqueue_42e686",0x42E686,0x42E6F2,((0x28,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x42,"open_cfw_bootloader_queue_send_4168a2",0x4168A2),(0x64,"open_cfw_bootloader_log_4176ce",0x4176CE))));CALLBACK=ctypes.CFUNCTYPE(None,ctypes.c_uint32)
class EventRuntimeServiceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"eventrt.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.init=d.open_cfw_bootloader_event_runtime_init_42e53c_portable;cls.init.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32)];cls.init.restype=ctypes.c_uint32;cls.step=d.open_cfw_bootloader_event_callback_loop_step_42e644_portable;cls.step.argtypes=[ctypes.c_uint32,ctypes.c_uint32,CALLBACK];cls.step.restype=ctypes.c_uint32;cls.enqueue=d.open_cfw_bootloader_event_callback_enqueue_42e686_portable;cls.enqueue.argtypes=[ctypes.c_uint32]*3;cls.enqueue.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_runtime_initialization(self):
  handles=(ctypes.c_uint32*4)(9,0,0,7);created=(ctypes.c_uint32*4)(1,2,0,4);self.assertEqual(self.init(handles,created),4);self.assertEqual(list(handles),[9,2,0,4])
 def test_callback_dispatch(self):
  calls=[]
  @CALLBACK
  def callback(v):calls.append(v)
  self.assertEqual(self.step(0,0x55,callback),1);self.assertEqual(calls,[0x55]);self.assertEqual(self.step(3,0x66,callback),0);self.assertEqual(calls,[0x55])
 def test_enqueue_status(self):
  self.assertEqual(self.enqueue(0,1,0),1);self.assertEqual(self.enqueue(1,0,9),0);self.assertEqual(self.enqueue(1,1,0),0);self.assertEqual(self.enqueue(1,1,3),2)
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
