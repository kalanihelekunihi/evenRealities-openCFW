import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_context_publish_42dca2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000;A=0x42DCA2;Z=0x42DD14;FN="open_cfw_bootloader_runtime_context_publish_42dca2"
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));RS=((0x2A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x38,"open_cfw_bootloader_queue_send_4168a2",0x4168A2),(0x5A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x68,"open_cfw_bootloader_runtime_transfer_41623a",0x41623A))
class ContextPublishTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"publish.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.publish=d.open_cfw_bootloader_runtime_context_publish_42dca2_portable;cls.publish.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];cls.publish.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_publish_paths(self):
  mask=ctypes.c_uint32(2);self.assertEqual(self.publish(0,0,ctypes.byref(mask)),0);self.assertEqual(mask.value,2);self.assertEqual(self.publish(1,3,ctypes.byref(mask)),0);self.assertEqual(mask.value,2);self.assertEqual(self.publish(1,0,ctypes.byref(mask)),1);self.assertEqual(mask.value,0x400002)
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes();rr=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":s,"symbol_type":"STT_NOTYPE","target_address":t} for o,s,t in RS]
  with tempfile.TemporaryDirectory() as temp:
   for profile,cc in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True);body,_=apollo_overlay.extract_in_place_function_section(obj,FN,runtime_address=A,relocation_configs=rr,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[A-BASE:Z-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
