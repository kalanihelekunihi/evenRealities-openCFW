import ctypes,hashlib
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest,zlib
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_misc_primitives_42d84c.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_stream_mode_42d84c",0x42D84C,0x42D88A),("open_cfw_bootloader_runtime_context_get_42d88a",0x42D88A,0x42D890),("open_cfw_bootloader_vector_handoff_42dc90",0x42DC90,0x42DCA2),("open_cfw_bootloader_crc32_table_42e1ec",0x42E1EC,0x42E220),("open_cfw_bootloader_terminal_mode_42e514",0x42E514,0x42E534))
class VectorState(ctypes.Structure):_fields_=[("vector_table",ctypes.c_uint32),("stack_pointer",ctypes.c_uint32),("reset_handler",ctypes.c_uint32)]
class MiscPrimitiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"misc.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.mode=dll.open_cfw_bootloader_stream_mode_42d84c_portable;cls.mode.argtypes=[ctypes.c_uint32];cls.mode.restype=ctypes.c_char_p;cls.context=dll.open_cfw_bootloader_runtime_context_get_42d88a_portable;cls.context.argtypes=[ctypes.c_void_p];cls.context.restype=ctypes.c_void_p;cls.vector=dll.open_cfw_bootloader_vector_handoff_42dc90_portable;cls.vector.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(VectorState)];cls.crc=dll.open_cfw_bootloader_crc32_table_42e1ec_portable;cls.crc.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];cls.crc.restype=ctypes.c_uint32;cls.terminal=dll.open_cfw_bootloader_terminal_mode_42e514_portable;cls.terminal.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];cls.terminal.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_mode_context_and_vector(self):
  self.assertEqual(self.mode(0),b"r");self.assertEqual(self.mode(1),b"r+");self.assertEqual(self.mode(1|(1<<8)),b"a+");self.assertEqual(self.mode(1|(1<<8)|(1<<10)),b"w+");self.assertEqual(self.context(0x1234),0x1234);vectors=(ctypes.c_uint32*2)(0x2007D000,0x0043297D);state=VectorState();self.vector(vectors,ctypes.byref(state));self.assertEqual((state.stack_pointer,state.reset_handler),(0x2007D000,0x0043297D))
 def test_crc_matches_standard_seed_contract(self):
  data=b"123456789";buf=(ctypes.c_uint8*len(data)).from_buffer_copy(data);self.assertEqual(self.crc(buf,len(data),None),zlib.crc32(data));seed=ctypes.c_uint32(0x12345678);self.assertEqual(self.crc(buf,len(data),ctypes.byref(seed)),zlib.crc32(data,seed.value))
 def test_terminal_modes(self):
  control=ctypes.c_uint32();self.assertEqual(self.terminal(0,ctypes.byref(control)),0);self.assertEqual(control.value,212);self.assertEqual(self.terminal(1,ctypes.byref(control)),0);self.assertEqual(control.value,27);self.assertEqual(self.terminal(2,ctypes.byref(control)),6)
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end in ITEMS:
     body,report=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=[],strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
