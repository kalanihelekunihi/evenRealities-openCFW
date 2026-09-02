import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_setup_42e278.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_event_runtime_setup_42e278",0x42E278,0x42E284,((0x02,"open_cfw_bootloader_event_runtime_init_42e53c",0x42E53C),(0x06,"open_cfw_bootloader_event_callback_dispatch_provider_42e284",0x42E284))),("open_cfw_bootloader_event_callback_dispatch_42e284",0x42E284,0x42E2A2,((0x02,"open_cfw_bootloader_runtime_value_4161c6",0x4161C6),(0x08,"open_cfw_bootloader_runtime_call_4161ce",0x4161CE),(0x12,"open_cfw_bootloader_runtime_value_4161c6",0x4161C6),(0x18,"open_cfw_bootloader_runtime_call_4161ce",0x4161CE))))
VOID=ctypes.CFUNCTYPE(None);VALUE=ctypes.CFUNCTYPE(ctypes.c_uint32);PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32)
class EventSetupTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"event-setup.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.dispatch=dll.open_cfw_bootloader_event_callback_dispatch_42e284_portable;cls.dispatch.argtypes=[VALUE,PAIR,VOID];cls.setup=dll.open_cfw_bootloader_event_runtime_setup_42e278_portable;cls.setup.argtypes=[VOID,VALUE,PAIR,VOID]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_dispatch_order_and_selectors(self):
  seen=[];values=iter((0x11,0x22))
  @VALUE
  def value():v=next(values);seen.append(("value",v));return v
  @PAIR
  def call(handle,selector):seen.append(("call",handle,selector))
  @VOID
  def callback():seen.append(("callback",))
  self.dispatch(value,call,callback);self.assertEqual(seen,[("value",0x11),("call",0x11,8),("callback",),("value",0x22),("call",0x22,0x30)])
 def test_setup_initializes_before_dispatch(self):
  seen=[]
  @VOID
  def initialize():seen.append("init")
  @VALUE
  def value():seen.append("value");return 7
  @PAIR
  def call(handle,selector):seen.append((handle,selector))
  @VOID
  def callback():seen.append("callback")
  self.setup(initialize,value,call,callback);self.assertEqual(seen,["init","value",(7,8),"callback","value",(7,0x30)])
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,specs in ITEMS:
     relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target} for offset,symbol,target in specs];body,_=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
