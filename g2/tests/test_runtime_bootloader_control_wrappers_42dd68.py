import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_control_wrappers_42dd68.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_runtime_context_wrapper_42dd68",0x42DD68,0x42DD70,((2,"open_cfw_bootloader_runtime_context_get_42d88a",0x42D88A),)),("open_cfw_bootloader_control_one_wrapper_42dd9a",0x42DD9A,0x42DDA4,((4,"open_cfw_bootloader_control_one_42e3e0",0x42E3E0),)),("open_cfw_bootloader_control_two_wrapper_42dda4",0x42DDA4,0x42DDAE,((4,"open_cfw_bootloader_control_two_42e412",0x42E412),)),("open_cfw_bootloader_control_bits_dispatch_42e1c4",0x42E1C4,0x42E1DA,((8,"open_cfw_bootloader_control_fault_42de58",0x42DE58),(0x10,"open_cfw_bootloader_control_terminal_loop_provider_42e1da",0x42E1DA))), ("open_cfw_bootloader_control_terminal_loop_42e1da",0x42E1DA,0x42E1EC,((4,"open_cfw_bootloader_control_terminal_42e444",0x42E444),(0x0C,"open_cfw_bootloader_runtime_notify_416378",0x416378))))
VALUE=ctypes.CFUNCTYPE(ctypes.c_uint32);ACTION=ctypes.CFUNCTYPE(None,ctypes.c_uint32)
class ControlWrapperTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"control.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.context=dll.open_cfw_bootloader_runtime_context_wrapper_42dd68_portable;cls.context.argtypes=[VALUE];cls.context.restype=ctypes.c_uint32;cls.one=dll.open_cfw_bootloader_control_one_wrapper_42dd9a_portable;cls.one.argtypes=[ACTION];cls.two=dll.open_cfw_bootloader_control_two_wrapper_42dda4_portable;cls.two.argtypes=[ACTION];cls.dispatch=dll.open_cfw_bootloader_control_bits_dispatch_42e1c4_portable;cls.dispatch.argtypes=[ctypes.c_uint32,ACTION,ACTION];cls.dispatch.restype=ctypes.c_uint32;cls.step=dll.open_cfw_bootloader_control_terminal_step_42e1da_portable;cls.step.argtypes=[ACTION,ACTION]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_context_and_constant_wrappers(self):
  @VALUE
  def value():return 0x12345678
  seen=[]
  @ACTION
  def action(argument):seen.append(argument)
  self.assertEqual(self.context(value),0x12345678);self.one(action);self.two(action);self.assertEqual(seen,[1,1])
 def test_bit_dispatch_and_terminal_step(self):
  seen=[]
  @ACTION
  def fault(argument):seen.append(("fault",argument))
  @ACTION
  def terminal(argument):seen.append(("terminal",argument))
  self.assertEqual(self.dispatch(0,fault,terminal),0);self.assertEqual(self.dispatch(1<<22,fault,terminal),1);self.assertEqual(self.dispatch(1<<23,fault,terminal),2);self.assertEqual(self.dispatch((1<<22)|(1<<23),fault,terminal),3);self.step(terminal,fault);self.assertEqual(seen[-2:],[('terminal',1),('fault',0xffffffff)])
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
