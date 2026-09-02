import ctypes,hashlib,random,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_chunked_source_compare_42da1e.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42DA1E;Z=0x42DAD0;BASE=0x410000;FN="open_cfw_bootloader_chunked_source_compare_42da1e";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x1A,"open_cfw_bootloader_compare_prepare_41e348",0x41E348),(0x42,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x7C,"open_cfw_bootloader_memory_compare_415758",0x415758),(0xA6,"open_cfw_bootloader_log_4176ce",0x4176CE));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
Reader=ctypes.CFUNCTYPE(None,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32)
class Model(ctypes.Structure):_fields_=[("read",Reader),("chunks",ctypes.c_uint32),("compared",ctypes.c_uint32)]
@Reader
def reader(dst,src,n):ctypes.memmove(dst,src,n)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"c.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.compare=d.open_cfw_bootloader_chunked_source_compare_42da1e_portable;cls.compare.argtypes=[ctypes.POINTER(Model),ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32];cls.compare.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def run_equal(self,n):
  data=bytes(random.Random(n).randrange(256)for _ in range(max(n,1)));a=(ctypes.c_uint8*max(n,1)).from_buffer_copy(data);b=(ctypes.c_uint8*max(n,1)).from_buffer_copy(data);s=Model(reader,0,0);self.assertEqual(self.compare(ctypes.byref(s),a,b,n),0);self.assertEqual((s.chunks,s.compared),((n+4095)//4096,n))
 def test_boundaries(self):
  for n in(0,1,4095,4096,4097,8192,9000):self.run_equal(n)
 def test_mismatch_stops_in_second_chunk(self):
  n=5000;data=bytearray((i*17)&255 for i in range(n));other=bytearray(data);other[4500]^=1;a=(ctypes.c_uint8*n).from_buffer_copy(data);b=(ctypes.c_uint8*n).from_buffer_copy(other);s=Model(reader,0,0);self.assertNotEqual(self.compare(ctypes.byref(s),a,b,n),0);self.assertEqual(s.chunks,2)
 def test_invalid_inputs(self):self.assertEqual(self.compare(None,None,None,1),-1)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"4addc6bfb9023df944da168fed7deb268b2de24817dd19865719e37f4131216b")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],4)
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
