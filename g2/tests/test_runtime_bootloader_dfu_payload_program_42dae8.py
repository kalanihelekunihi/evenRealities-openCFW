import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_dfu_payload_program_42dae8.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42DAE8;Z=0x42DC90;BASE=0x410000;FN="open_cfw_bootloader_dfu_payload_program_42dae8";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x18,"open_cfw_bootloader_chunked_indirect_visit_42d9f0",0x42D9F0),(0x40,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x46,"open_cfw_bootloader_stream_mode_42d84c",0x42D84C),(0x52,"open_cfw_bootloader_file_open_4153a4",0x4153A4),(0x7A,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x88,"open_cfw_bootloader_file_prepare_4154d2",0x4154D2),(0xA0,"open_cfw_bootloader_log_4176ce",0x4176CE),(0xD8,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x100,"open_cfw_bootloader_file_read_415484",0x415484),(0x122,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x142,"open_cfw_bootloader_chunked_source_compare_42da1e",0x42DA1E),(0x164,"open_cfw_bootloader_log_4176ce",0x4176CE),(0x180,"open_cfw_bootloader_file_close_415446",0x415446),(0x19E,"open_cfw_bootloader_log_4176ce",0x4176CE));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("encoded_size",ctypes.c_uint32),("start_address",ctypes.c_uint32),("chunk_size",ctypes.c_uint32),("open_result",ctypes.c_uint32),("read_results",ctypes.POINTER(ctypes.c_uint32)),("compare_results",ctypes.POINTER(ctypes.c_uint32)),("result_count",ctypes.c_uint32),("read_calls",ctypes.c_uint32),("program_calls",ctypes.c_uint32),("compare_calls",ctypes.c_uint32),("short_read_logs",ctypes.c_uint32),("compare_error_logs",ctypes.c_uint32),("close_calls",ctypes.c_uint32),("handle",ctypes.c_uint32),("final_address",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"program.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.program=d.open_cfw_bootloader_dfu_payload_program_42dae8_portable;cls.program.argtypes=[ctypes.POINTER(Model)];cls.program.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_open_failure_and_invalid(self):
  self.assertEqual(self.program(None),0xffffffff);m=Model(encoded_size=64,chunk_size=16);self.assertEqual(self.program(ctypes.byref(m)),1)
 def test_full_chunks_remainder_program_compare_and_close(self):
  reads=(ctypes.c_uint32*3)(32,31,6);compares=(ctypes.c_uint32*3)(0,1,0);m=Model(encoded_size=32+70,start_address=0x1000,chunk_size=32,open_result=9,read_results=reads,compare_results=compares,result_count=3);self.assertEqual(self.program(ctypes.byref(m)),0);self.assertEqual((m.read_calls,m.program_calls,m.compare_calls,m.short_read_logs,m.compare_error_logs,m.close_calls,m.handle,m.final_address),(3,3,3,1,1,1,0,0x1046))
 def test_result_bound(self):
  x=(ctypes.c_uint32*1)(4);m=Model(encoded_size=40,chunk_size=4,open_result=1,read_results=x,compare_results=x,result_count=1);self.assertEqual(self.program(ctypes.byref(m)),2)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"8bec7ec7631e231c2c79d32f04f64eac3e12a99c3a80c879b441bbf6a62dfd82")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],14);self.assertEqual(r["unrelocated_sha256"],"3718f9c7011258ecc5e206c225615ab863b422edaef09bc6063fffe2490151c1")
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
