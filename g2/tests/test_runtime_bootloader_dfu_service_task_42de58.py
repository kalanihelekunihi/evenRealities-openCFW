import ctypes,hashlib,importlib.util,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_dfu_service_task_42de58.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42DE58;Z=0x42E104;BASE=0x410000;FN="open_cfw_bootloader_dfu_service_task_42de58";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
spec=importlib.util.spec_from_file_location("dfu_task_integrator",ROOT/"tools/integrate_g2_bootloader_dfu_service_task_42de58.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in mod.RS];FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
class Model(ctypes.Structure):_fields_=[("receive_status",ctypes.c_uint32),("command",ctypes.c_uint32),("active_vector",ctypes.c_uint32),("image_open",ctypes.c_uint32),("image_read",ctypes.c_uint32),("header_flags",ctypes.c_uint32),("crc_ok",ctypes.c_uint32),("active_vector_word",ctypes.c_uint32),("alternate_pointer",ctypes.c_uint32),("close_calls",ctypes.c_uint32),("enable_calls",ctypes.c_uint32),("disable_calls",ctypes.c_uint32),("crc_calls",ctypes.c_uint32),("program_calls",ctypes.c_uint32),("handoff_calls",ctypes.c_uint32),("loop_again",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"task.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.step=d.open_cfw_bootloader_dfu_service_task_42de58_portable;cls.step.argtypes=[ctypes.POINTER(Model)];cls.step.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_image_open_read_crc_program_and_handoff(self):
  m=Model(command=1,image_open=3,image_read=32,header_flags=1<<26,crc_ok=1,active_vector_word=1<<29);self.assertEqual(self.step(ctypes.byref(m)),0);self.assertEqual((m.close_calls,m.crc_calls,m.program_calls,m.disable_calls,m.handoff_calls),(1,1,1,1,1))
 def test_failures_and_alternate(self):
  m=Model(command=1,image_open=0);self.assertEqual(self.step(ctypes.byref(m)),0);self.assertEqual(m.enable_calls,1);m=Model(command=7,alternate_pointer=7,active_vector_word=1<<29);self.assertEqual(self.step(ctypes.byref(m)),0);self.assertEqual((m.disable_calls,m.handoff_calls),(1,1))
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"52e1f7a3ed50f4a8167463ae705cccee6ac690db1de524927a2eca9eb424557f")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],29);self.assertEqual(r["unrelocated_sha256"],"759dc2f405b33a3e61e91d43484cc390e102b717c3e6a7c7d4729f1705b112b8")
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
