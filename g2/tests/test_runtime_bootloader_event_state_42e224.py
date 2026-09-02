import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_state_42e224.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_retained_state_probe_42e224",0x42E224,0x42E254,((0x1A,"open_cfw_bootloader_log_4176ce",0x4176CE),)),("open_cfw_bootloader_event_flags_init_42e254",0x42E254,0x42E276,((0x06,"open_cfw_bootloader_event_flags_create_4164da",0x4164DA),(0x12,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8))),("open_cfw_bootloader_guard_context_init_42e39c",0x42E39C,0x42E3CA,((0x02,"open_cfw_bootloader_runtime_prepare_416058",0x416058),(0x0E,"open_cfw_bootloader_runtime_dispatch_4160fe",0x4160FE),(0x1A,"open_cfw_bootloader_allocation_failure_41b2f8",0x41B2F8),(0x28,"open_cfw_bootloader_runtime_finalize_4160b0",0x4160B0))),("open_cfw_bootloader_control_one_wait_42e3e0",0x42E3E0,0x42E412,((0x0E,"open_cfw_bootloader_event_wait_4162c4",0x4162C4),(0x2C,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_control_two_publish_42e412",0x42E412,0x42E444,((0x1C,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x2C,"open_cfw_bootloader_event_bits_set_41652e",0x41652E))))
UNARY=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32);DISPATCH=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32);WAIT=DISPATCH;PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32);VOID=ctypes.CFUNCTYPE(None)
class EventStateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"event-state.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.probe=d.open_cfw_bootloader_retained_state_probe_42e224_portable;cls.probe.restype=ctypes.c_uint32;cls.init=d.open_cfw_bootloader_event_flags_init_42e254_portable;cls.init.argtypes=[ctypes.POINTER(ctypes.c_uint32),UNARY];cls.init.restype=ctypes.c_uint32;cls.wait=d.open_cfw_bootloader_control_one_wait_42e3e0_portable;cls.wait.argtypes=[ctypes.c_uint32,WAIT];cls.wait.restype=ctypes.c_uint32;cls.publish=d.open_cfw_bootloader_control_two_publish_42e412_portable;cls.publish.argtypes=[ctypes.c_uint32,ctypes.c_uint32,PAIR]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_probe_init_wait_publish(self):
  self.assertEqual(self.probe(0x55555555),1);self.assertEqual(self.probe(0),0)
  @UNARY
  def create(value):return 0x44 if value==0 else 0
  slot=ctypes.c_uint32();self.assertEqual(self.init(ctypes.byref(slot),create),1);self.assertEqual(slot.value,0x44)
  results=iter((0,0x800000))
  @WAIT
  def wait(handle,mask,timeout):self.assertEqual((handle,mask,timeout),(7,1,0xffffffff));return next(results)
  self.assertEqual(self.wait(7,wait),2)
  seen=[]
  @PAIR
  def publish(handle,mask):seen.append((handle,mask))
  self.publish(0x44,5,publish);self.assertEqual(seen,[(0x44,0x20)])
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
