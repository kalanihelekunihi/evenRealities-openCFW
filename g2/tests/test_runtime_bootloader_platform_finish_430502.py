import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_platform_finish_430502.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x430502;Z=0x430610;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_platform_finish_430502";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x12,"open_cfw_bootloader_hw_context_claim_42c4c6",0x42C4C6),(0x26,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x3E,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x50,"open_cfw_bootloader_hw_config_transaction_42c988",0x42C988),(0x60,"open_cfw_bootloader_hw_instance_configure_42cc34",0x42CC34),(0x6A,"open_cfw_bootloader_hw_context_enable_42c538",0x42C538),(0x74,"open_cfw_bootloader_hw_config_retry_43048e",0x43048E),(0xA6,"open_cfw_bootloader_event_object_create_416610",0x416610),(0xCA,"open_cfw_bootloader_hw_interrupt_enable_42c63a",0x42C63A),(0xD0,"open_cfw_bootloader_nvic_enable_bit_430470",0x430470),(0xDE,"open_cfw_bootloader_event_flags_create_416762",0x416762),(0x104,"open_cfw_bootloader_log_4176ce",0x4176CE));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Slot(ctypes.Structure):_fields_=[("active",ctypes.c_uint8),("event_present",ctypes.c_uint8),("event_create_success",ctypes.c_uint8),("first_callback_status",ctypes.c_uint32),("second_callback_status",ctypes.c_uint32),("context_enable_status",ctypes.c_uint32),("claim_calls",ctypes.c_uint32),("configure_calls",ctypes.c_uint32),("retry_calls",ctypes.c_uint32)]
class Model(ctypes.Structure):_fields_=[("slot",Slot*8),("global_event_create_success",ctypes.c_uint8),("interrupt_enable_calls",ctypes.c_uint32),("nvic_enable_calls",ctypes.c_uint32),("global_event_create_calls",ctypes.c_uint32),("log_calls",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"finish.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.finish=d.open_cfw_bootloader_platform_finish_430502_portable;cls.finish.argtypes=[ctypes.POINTER(Model)];cls.finish.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_empty_and_multi_slot_success(self):
  s=Model();s.global_event_create_success=1;self.assertEqual(self.finish(ctypes.byref(s)),0);self.assertEqual((s.interrupt_enable_calls,s.nvic_enable_calls,s.global_event_create_calls,s.log_calls),(1,1,1,0))
  s=Model();s.global_event_create_success=1
  for i,status in ((1,3),(5,7)):
   s.slot[i].active=1;s.slot[i].event_create_success=1;s.slot[i].context_enable_status=status
  self.assertEqual(self.finish(ctypes.byref(s)),7)
  for i in(1,5):self.assertEqual((s.slot[i].event_present,s.slot[i].claim_calls,s.slot[i].configure_calls,s.slot[i].retry_calls),(1,1,2,1))
 def test_missing_slot_event_fails_before_hardware_setup(self):
  s=Model();s.global_event_create_success=1;s.slot[2].active=1;self.assertEqual(self.finish(ctypes.byref(s)),1);self.assertEqual((s.slot[2].claim_calls,s.interrupt_enable_calls),(0,0))
 def test_callback_failures_stop_in_order(self):
  for first,second in ((1,0),(0,1)):
   s=Model();s.global_event_create_success=1;s.slot[0].active=1;s.slot[0].event_present=1;s.slot[0].first_callback_status=first;s.slot[0].second_callback_status=second;self.assertEqual(self.finish(ctypes.byref(s)),1);self.assertEqual(s.slot[0].claim_calls,1);self.assertEqual((s.slot[0].configure_calls,s.slot[0].retry_calls),(0,0));self.assertEqual(s.interrupt_enable_calls,0)
 def test_global_event_failure_logs_and_returns_failure(self):
  s=Model();self.assertEqual(self.finish(ctypes.byref(s)),1);self.assertEqual((s.interrupt_enable_calls,s.nvic_enable_calls,s.global_event_create_calls,s.log_calls),(1,1,1,1))
 def test_invalid_model(self):self.assertEqual(self.finish(None),1)
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"f92c35acae4e7f10f79008020f00bb4607f39ff6b09545fbbbc93348b6873195");analogue=MAIN.read_bytes()[0x50423A-MAIN_BASE:0x50423A-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),196)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],12);self.assertEqual(r["unrelocated_sha256"],"bad372fa5e2a442fcbf1d4e7a767aed113b369aeeaffb8d5cb4e3fd107da4b99")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
