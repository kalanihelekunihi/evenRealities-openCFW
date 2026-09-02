import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_descriptor_register_430280.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x430280;Z=0x4303BC;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_descriptor_register_430280";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x32,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x5E,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x86,"open_cfw_bootloader_memset_415ff4",0x415FF4),(0xA4,"open_cfw_bootloader_irq_mask_control_41dcca",0x41DCCA),(0xAC,"open_cfw_bootloader_irq_mask_apply_41de3c",0x41DE3C),(0xBE,"open_cfw_bootloader_irq_handler_bind_41e000",0x41E000),(0xC8,"open_cfw_bootloader_irq_state_publish_41da84",0x41DA84),(0xDE,"open_cfw_bootloader_scb_priority_nibble_43025c",0x43025C),(0xEE,"open_cfw_bootloader_nvic_enable_bit_430240",0x430240),(0x110,"open_cfw_bootloader_callback_register_41d92c",0x41D92C),(0x12E,"open_cfw_bootloader_boolean_route_41d9aa",0x41D9AA));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Record(ctypes.Structure):_fields_=[("identifier",ctypes.c_uint32),("type",ctypes.c_uint8),("enabled",ctypes.c_uint8),("mode",ctypes.c_uint8),("payload",ctypes.c_uint32)]
class Model(ctypes.Structure):_fields_=[("callback_calls",ctypes.c_uint32),("boolean_calls",ctypes.c_uint32),("irq_setup_calls",ctypes.c_uint32),("priority_calls",ctypes.c_uint32),("enable_calls",ctypes.c_uint32),("last_mask_word",ctypes.c_uint32),("last_mask_bit",ctypes.c_uint32),("last_boolean",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"descriptor.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.register=d.open_cfw_bootloader_descriptor_register_430280_portable;cls.register.argtypes=[ctypes.POINTER(Record),ctypes.c_uint32,ctypes.POINTER(Model)];cls.register.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_invalid_inputs(self):
  s=Model();r=Record();self.assertEqual(self.register(None,1,ctypes.byref(s)),0xFFFFFFFF);self.assertEqual(self.register(ctypes.byref(r),0,ctypes.byref(s)),0xFFFFFFFF);self.assertEqual(self.register(ctypes.byref(r),1,None),0xFFFFFFFF)
 def test_type_routes_and_boolean_normalization(self):
  records=(Record*4)();records[0].type=1;records[0].enabled=1;records[1].type=1;records[1].enabled=2;records[2].type=4;records[3].type=3;s=Model();self.assertEqual(self.register(records,4,ctypes.byref(s)),0);self.assertEqual((s.callback_calls,s.boolean_calls,s.last_boolean),(3,2,0));self.assertEqual(s.irq_setup_calls,0)
 def test_type_two_interrupt_setup_and_gates(self):
  records=(Record*3)();records[0].type=2;records[0].identifier=95;records[0].mode=3;records[0].payload=1;records[1].type=2;records[1].mode=0;records[1].payload=1;records[2].type=2;records[2].mode=1;records[2].payload=0;s=Model();self.assertEqual(self.register(records,3,ctypes.byref(s)),0);self.assertEqual(s.callback_calls,3);self.assertEqual((s.irq_setup_calls,s.priority_calls,s.enable_calls),(1,1,1));self.assertEqual((s.last_mask_word,s.last_mask_bit),(2,31))
 def test_mask_boundaries(self):
  for identifier,word,bit in ((0,0,0),(31,0,31),(32,1,0),(223,6,31)):
   r=Record(identifier,2,0,1,1);s=Model();self.register(ctypes.byref(r),1,ctypes.byref(s));self.assertEqual((s.last_mask_word,s.last_mask_bit),(word,bit))
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"41b2abc6111a25a5b0ee15e4c3e877aaa486b631855ca3dd75fb388d55dd1391");analogue=MAIN.read_bytes()[0x53A454-MAIN_BASE:0x53A454-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),285)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],11);self.assertEqual(r["unrelocated_sha256"],"c9ef6ec35809b9ae523a8708c7db831ebb14f56991a1ba3f05b6e9fd7fcf4625")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
