import ctypes, hashlib, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_handle_command_42eff4.c"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
sys.path.insert(0,str(ROOT/"tools")); import apollo_overlay  # noqa: E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding",
       "-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables",
       "-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident",
       "-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
          Path("/opt/homebrew/opt/llvm@22/bin/clang"))
FUNCTION="open_cfw_bootloader_hw_handle_command_42eff4"

class Handle(ctypes.Structure): _fields_=[("word0",ctypes.c_uint32),("word1",ctypes.c_uint32)]

class TestCommand(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(); lib=Path(cls.tmp.name)/"x.so"; cc=shutil.which("cc") or shutil.which("clang")
  subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True)
  cls.call=ctypes.CDLL(str(lib)).open_cfw_bootloader_hw_handle_command_42eff4_portable
  cls.call.argtypes=[ctypes.POINTER(Handle),ctypes.POINTER(ctypes.c_uint32)];cls.call.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def test_routes(self):
  command=ctypes.c_uint32(9); bad=Handle(); good=Handle(0x01AFAFAF,0)
  self.assertEqual(self.call(ctypes.byref(bad),ctypes.byref(command)),2);self.assertEqual(command.value,9)
  self.assertEqual(self.call(ctypes.byref(good),ctypes.byref(command)),0);self.assertEqual(command.value,55)
 def test_exact(self):
  boot=BOOT.read_bytes();main=MAIN.read_bytes();stock=boot[0x1eff4:0x1f014];analogue=main[0x55e070-0x437fe0:0x55e090-0x437fe0]
  self.assertEqual(hashlib.sha256(stock).hexdigest(),"ed0aedd4d0d69cedbcae932b154d2ed9f290d4c95bc0f3f06f8135539c19ec6f");self.assertEqual(stock,analogue)
  with tempfile.TemporaryDirectory() as d:
   for cc in PROFILES:
    obj=Path(d)/(cc.name+str(len(str(cc)))+".o");subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True)
    linked,report=apollo_overlay.extract_in_place_function_section(obj,FUNCTION,runtime_address=0x42EFF4,relocation_configs=[],strict_relocation_contract=True,allow_discarded_alloc_sections=True)
    self.assertEqual(linked,stock);self.assertEqual(report["relocation_count"],0)
 def test_reviewable(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text);self.assertIn(FUNCTION,text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)

if __name__=="__main__":unittest.main()
