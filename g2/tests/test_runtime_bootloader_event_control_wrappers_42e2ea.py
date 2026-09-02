import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_event_control_wrappers_42e2ea.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));ITEMS=(("open_cfw_bootloader_event_wait_one_wrapper_42e2ea",0x42E2EA,0x42E2F8,0x08,"open_cfw_bootloader_event_wait_42e2a2",0x42E2A2),("open_cfw_bootloader_guarded_context_teardown_42e3ca",0x42E3CA,0x42E3E0,0x0C,"open_cfw_bootloader_guarded_action_416200",0x416200),("open_cfw_bootloader_event_bit_set_42e444",0x42E444,0x42E458,0x0E,"open_cfw_bootloader_event_bits_set_41652e",0x41652E))
PAIR=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32);ACTION=ctypes.CFUNCTYPE(None,ctypes.c_uint32)
class EventControlWrapperTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"event.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.wait=dll.open_cfw_bootloader_event_wait_one_wrapper_42e2ea_portable;cls.wait.argtypes=[ctypes.c_uint32,PAIR];cls.teardown=dll.open_cfw_bootloader_guarded_context_teardown_42e3ca_portable;cls.teardown.argtypes=[ctypes.POINTER(ctypes.c_uint32),ACTION];cls.teardown.restype=ctypes.c_uint32;cls.set_bit=dll.open_cfw_bootloader_event_bit_set_42e444_portable;cls.set_bit.argtypes=[ctypes.c_uint32,ctypes.c_uint32,PAIR]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_wait_and_event_bit(self):
  seen=[]
  @PAIR
  def pair(first,second):seen.append((first,second))
  self.wait(0x44,pair);self.set_bit(0x55,7,pair);self.assertEqual(seen,[(0x44,1),(0x55,0x80)])
 def test_guarded_teardown(self):
  seen=[]
  @ACTION
  def action(value):seen.append(value)
  context=ctypes.c_uint32();self.assertEqual(self.teardown(ctypes.byref(context),action),0);context.value=0x1234;self.assertEqual(self.teardown(ctypes.byref(context),action),1);self.assertEqual((context.value,seen),(0,[0x1234]))
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,offset,symbol,target in ITEMS:
     relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target}];body,_=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
