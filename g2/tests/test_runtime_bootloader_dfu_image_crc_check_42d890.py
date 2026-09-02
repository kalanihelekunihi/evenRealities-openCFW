import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_dfu_image_crc_check_42d890.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42D890;Z=0x42D9F0;BASE=0x410000;FN="open_cfw_bootloader_dfu_image_crc_check_42d890";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x18,"open_cfw_bootloader_stream_mode_42d84c",0x42D84C),(0x24,"open_cfw_bootloader_file_open_4153a4",0x4153A4),(0x4A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x58,"open_cfw_bootloader_file_prepare_4154d2",0x4154D2),(0x70,"open_cfw_bootloader_file_read_415484",0x415484),(0x98,"open_cfw_bootloader_log_4176ce",0x4176CE),(0xA6,"open_cfw_bootloader_crc32_table_42e1ec",0x42E1EC),(0xDE,"open_cfw_bootloader_file_read_415484",0x415484),(0x102,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x10C,"open_cfw_bootloader_crc32_table_42e1ec",0x42E1EC),(0x11A,"open_cfw_bootloader_file_close_415446",0x415446),(0x146,"open_cfw_bootloader_log_4176ce",0x4176CE));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("encoded_size",ctypes.c_uint32),("expected_crc",ctypes.c_uint32),("chunk_size",ctypes.c_uint32),("open_result",ctypes.c_uint32),("read_results",ctypes.POINTER(ctypes.c_uint32)),("crc_results",ctypes.POINTER(ctypes.c_uint32)),("read_result_count",ctypes.c_uint32),("read_calls",ctypes.c_uint32),("short_read_logs",ctypes.c_uint32),("close_calls",ctypes.c_uint32),("handle",ctypes.c_uint32),("final_crc",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"crc.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.check=d.open_cfw_bootloader_dfu_image_crc_check_42d890_portable;cls.check.argtypes=[ctypes.POINTER(Model)];cls.check.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_open_rejection_and_invalid_inputs(self):
  self.assertEqual(self.check(None),0);m=Model(chunk_size=64,open_result=0);self.assertEqual(self.check(ctypes.byref(m)),0);self.assertEqual(m.close_calls,0);m=Model(chunk_size=0,open_result=1);self.assertEqual(self.check(ctypes.byref(m)),0)
 def test_full_chunks_remainder_short_read_and_match(self):
  reads=(ctypes.c_uint32*3)(64,63,10);crcs=(ctypes.c_uint32*3)(1,2,0x12345678);m=Model(encoded_size=8+138,expected_crc=0x12345678,chunk_size=64,open_result=9,read_results=reads,crc_results=crcs,read_result_count=3);self.assertEqual(self.check(ctypes.byref(m)),1);self.assertEqual((m.read_calls,m.short_read_logs,m.close_calls,m.handle,m.final_crc),(3,1,1,0,0x12345678))
 def test_crc_mismatch(self):
  reads=(ctypes.c_uint32*1)(12);crcs=(ctypes.c_uint32*1)(7);m=Model(encoded_size=20,expected_crc=8,chunk_size=64,open_result=1,read_results=reads,crc_results=crcs,read_result_count=1);self.assertEqual(self.check(ctypes.byref(m)),0);self.assertEqual(m.close_calls,1)
 def test_dual_toolchain_exact_and_caller(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"b0ddd79ec823f1045ba1d689a2b9199a103a3c10afcd2d34cab9a66af914f82f")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],12);self.assertEqual(r["unrelocated_sha256"],"fce1f2d8b577fe200de04a0350123dcd15365db537253e93fcef3fec5a29ac0a")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
