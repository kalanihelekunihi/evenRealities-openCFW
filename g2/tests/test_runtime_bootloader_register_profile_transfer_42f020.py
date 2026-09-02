import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_register_profile_transfer_42f020.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42F020;Z=0x42F14E;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_register_profile_transfer_42f020";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x3E,"open_cfw_bootloader_mode_query_41bf84",0x41BF84),(0x4C,"open_cfw_bootloader_mode_enable_route_4222f0",0x4222F0),(0x11E,"open_cfw_bootloader_clock_config_422364",0x422364),(0x124,"open_cfw_bootloader_delay_status_41c17a",0x41C17A));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("header",ctypes.c_uint32),("valid",ctypes.c_uint8),("control",ctypes.c_uint32),("field",ctypes.c_uint32*11),("aux",ctypes.c_uint32),("hw_control",ctypes.c_uint32),("hw_field",ctypes.c_uint32*11),("hw_aux",ctypes.c_uint32),("route_status",ctypes.c_uint32),("mode_query_calls",ctypes.c_uint32),("clock_calls",ctypes.c_uint32),("delay_calls",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"profile.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.transfer=d.open_cfw_bootloader_register_profile_transfer_42f020_portable;cls.transfer.argtypes=[ctypes.POINTER(Model),ctypes.c_uint32,ctypes.c_uint32];cls.transfer.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def model(self):s=Model();s.header=0x81AFAFAF;return s
 def test_validation_and_operation_statuses(self):
  self.assertEqual(self.transfer(None,0,0),2);s=Model();s.header=0x1234;self.assertEqual(self.transfer(ctypes.byref(s),0,0),2);s=self.model();self.assertEqual(self.transfer(ctypes.byref(s),3,0),6);self.assertEqual(self.transfer(ctypes.byref(s),0,1),7)
 def test_apply_disabled_only_queries_mode(self):
  s=self.model();self.assertEqual(self.transfer(ctypes.byref(s),0,0),0);self.assertEqual(s.mode_query_calls,1);self.assertEqual((s.clock_calls,s.delay_calls),(0,0))
 def test_apply_profile_and_route_failure(self):
  s=self.model();s.valid=1;s.control=0x55;s.aux=0xAA
  for i in range(11):s.field[i]=0x100+i
  self.assertEqual(self.transfer(ctypes.byref(s),0,1),0);self.assertEqual((s.hw_control,s.hw_aux,s.valid),(0x55,0xAA,0));self.assertEqual(list(s.hw_field),[0x100+i for i in range(11)])
  s=self.model();s.valid=1;s.route_status=9;self.assertEqual(self.transfer(ctypes.byref(s),0,1),9);self.assertEqual(s.valid,1)
 def test_capture_enabled_and_disabled(self):
  s=self.model();s.hw_control=0x77;s.hw_aux=0x88
  for i in range(11):s.hw_field[i]=0x200+i
  self.assertEqual(self.transfer(ctypes.byref(s),1,1),0);self.assertEqual((s.control,s.aux,s.valid),(0x77,0x88,1));self.assertEqual(list(s.field),[0x200+i for i in range(11)]);self.assertEqual((s.clock_calls,s.delay_calls),(1,1))
  s=self.model();s.control=5;self.assertEqual(self.transfer(ctypes.byref(s),2,0),0);self.assertEqual((s.control,s.valid,s.clock_calls,s.delay_calls),(5,0,1,1))
 def test_low_byte_operation_semantics(self):
  s=self.model();self.assertEqual(self.transfer(ctypes.byref(s),0x101,0),0);self.assertEqual((s.clock_calls,s.delay_calls),(1,1))
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"2e6cca806f60cc19024673c46f635245eaea0c8e7aff23580b1a8cf15e487a73");analogue=MAIN.read_bytes()[0x55E09C-MAIN_BASE:0x55E09C-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),292)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],4);self.assertEqual(r["unrelocated_sha256"],"7019743d54c61b4d148d591856d90a4c23d482770fc7938db8b4b374ef53278c")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
