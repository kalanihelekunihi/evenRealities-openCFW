import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_control_services_42bf54.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_hardware_readiness_gate_42bf54",0x42BF54,0x42BFA4,((0x14,"open_cfw_bootloader_mode_query_41bf84",0x41BF84),(0x26,"open_cfw_bootloader_float_probe_41ca2c",0x41CA2C),(0x38,"open_cfw_bootloader_delay_status_change_41d21c",0x41D21C))),("open_cfw_bootloader_event_wait_mask_42e2a2",0x42E2A2,0x42E2EA,((0x0E,"open_cfw_bootloader_runtime_transfer_41623a",0x41623A),(0x1E,"open_cfw_bootloader_runtime_flags_wait_416590",0x416590),(0x40,"open_cfw_bootloader_log_4176ce",0x4176CE))),("open_cfw_bootloader_aligned_guarded_dispatch_42e4a0",0x42E4A0,0x42E4F4,((0x1C,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0x22,"open_cfw_bootloader_runtime_lock_41bd92",0x41BD92),(0x30,"open_cfw_bootloader_guarded_call_cleanup_42e8a4",0x42E8A4),(0x36,"open_cfw_bootloader_runtime_unlock_41bde4",0x41BDE4))),("open_cfw_bootloader_register_power_toggle_42f1c8",0x42F1C8,0x42F204,((0x16,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0),(0x1C,"open_cfw_bootloader_power_control_41c838",0x41C838),(0x24,"open_cfw_bootloader_power_control_41c838",0x41C838),(0x2A,"open_cfw_bootloader_delay_cycles_41d1c0",0x41D1C0))))
UNARY=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32);WAIT=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32);DISPATCH=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32)
class ControlServiceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"controls.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.ready=d.open_cfw_bootloader_hardware_readiness_gate_42bf54_portable;cls.ready.argtypes=[ctypes.c_uint32]*5;cls.ready.restype=ctypes.c_uint32;cls.wait=d.open_cfw_bootloader_event_wait_mask_42e2a2_portable;cls.wait.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,WAIT,UNARY];cls.wait.restype=ctypes.c_uint32;cls.dispatch=d.open_cfw_bootloader_aligned_guarded_dispatch_42e4a0_portable;cls.dispatch.argtypes=[ctypes.c_uint32]*5+[DISPATCH];cls.dispatch.restype=ctypes.c_uint32;cls.toggle=d.open_cfw_bootloader_register_power_toggle_42f1c8_portable;cls.toggle.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),UNARY,UNARY]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_readiness_precedence(self):
  self.assertEqual(self.ready(0,0,0,0,0),0);self.assertEqual(self.ready(0,0,0,0,1),4)
  for args in ((1,0,0,0,0),(0,1,0,0,0),(0,0,1,0,0),(0,0,0,1,0)):self.assertEqual(self.ready(*args),1)
 def test_event_wait_mask(self):
  calls=[]
  @UNARY
  def transfer(v):calls.append(("transfer",v));return 0
  @WAIT
  def wait(h,m,t):calls.append(("wait",h,m,t));return m
  self.assertEqual(self.wait(9,3,7,wait,transfer),1);self.assertEqual(calls,[("transfer",9),("wait",7,8,0x4E20)])
  @WAIT
  def miss(_h,_m,_t):return 0
  self.assertEqual(self.wait(9,3,7,miss,transfer),0)
 def test_aligned_dispatch(self):
  calls=[]
  @DISPATCH
  def dispatch(*args):calls.append(args);return 3
  self.assertEqual(self.dispatch(1,2,0x40000C,4,0x77,dispatch),0x08000103);self.assertEqual(calls,[(1,1,2,3,4)])
  self.assertEqual(self.dispatch(1,2,0x400002,4,0x77,dispatch),0x77);self.assertEqual(len(calls),1)
 def test_register_power_order(self):
  calls=[]
  @UNARY
  def power(v):calls.append(("power",v));return 0
  @UNARY
  def delay(v):calls.append(("delay",v));return 0
  control=ctypes.c_uint32(0x10);self.toggle(1,ctypes.byref(control),power,delay);self.assertEqual((control.value,calls),(0x11,[("delay",5),("power",1)]));calls.clear();self.toggle(0,ctypes.byref(control),power,delay);self.assertEqual((control.value,calls),(0x10,[("power",0),("delay",5)]))
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
