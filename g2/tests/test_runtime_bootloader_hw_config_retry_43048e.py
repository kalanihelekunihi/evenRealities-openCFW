import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_config_retry_43048e.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x43048E;Z=0x430502;BASE=0x410000;FN="open_cfw_bootloader_hw_config_retry_43048e";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x24,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x36,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x40,"open_cfw_bootloader_delay_us_41f9d8",0x41F9D8),(0x5E,"open_cfw_bootloader_hw_config_transaction_42c988",0x42C988));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[(n,ctypes.c_uint32)for n in("callback_registrations","attempts","delay_calls","last_delay_us")]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"r.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.retry=d.open_cfw_bootloader_hw_config_retry_43048e_portable;cls.retry.argtypes=[ctypes.POINTER(Model),ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32];cls.retry.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_success_first_attempt_and_channel_callbacks(self):
  s=Model();v=(ctypes.c_uint32*1)(0);self.assertEqual(self.retry(ctypes.byref(s),4,v,1),0);self.assertEqual((s.callback_registrations,s.attempts,s.delay_calls),(2,1,0))
 def test_retries_then_success(self):
  s=Model();v=(ctypes.c_uint32*3)(7,3,0);self.assertEqual(self.retry(ctypes.byref(s),2,v,3),0);self.assertEqual((s.attempts,s.delay_calls,s.last_delay_us),(3,2,10))
 def test_timeout_is_bounded(self):
  s=Model();self.assertEqual(self.retry(ctypes.byref(s),0,None,0),4);self.assertEqual((s.attempts,s.delay_calls),(1000,999))
 def test_null_state_fails(self):self.assertEqual(self.retry(None,4,None,0),4)
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"6ba3fb6ddde5fa56fd43fc1f7f717bcc7cf201df2ae6af1b86d20bdde8404dbb")
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],4)
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
