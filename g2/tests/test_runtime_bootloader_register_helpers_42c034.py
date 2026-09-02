import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_register_helpers_42c034.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_hw_status_route_42c034",0x42C034,0x42C076),("open_cfw_bootloader_hw_error_classify_42c076",0x42C076,0x42C0B2),("open_cfw_bootloader_hw_interrupt_enable_42c63a",0x42C63A,0x42C672),("open_cfw_bootloader_hw_interrupt_status_get_42c672",0x42C672,0x42C6B6),("open_cfw_bootloader_hw_interrupt_clear_42c6b6",0x42C6B6,0x42C6E4),("open_cfw_bootloader_nvic_enable_bit_430240",0x430240,0x43025C),("open_cfw_bootloader_scb_priority_nibble_43025c",0x43025C,0x430280),("open_cfw_bootloader_nvic_enable_bit_430470",0x430470,0x43048E))
class Handle(ctypes.Structure):_fields_=[("word0",ctypes.c_uint32),("instance",ctypes.c_uint32)]
class Instance(ctypes.Structure):_fields_=[("control",ctypes.c_uint32),("status",ctypes.c_uint32),("clear",ctypes.c_uint32)]
class RegisterHelperTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"register.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.route=dll.open_cfw_bootloader_hw_status_route_42c034_portable;cls.route.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_uint32];cls.route.restype=ctypes.c_uint32;cls.classify=dll.open_cfw_bootloader_hw_error_classify_42c076_portable;cls.classify.argtypes=[ctypes.c_uint32,ctypes.c_uint32];cls.classify.restype=ctypes.c_uint32;cls.enable=dll.open_cfw_bootloader_hw_interrupt_enable_42c63a_portable;cls.enable.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(Instance)];cls.enable.restype=ctypes.c_uint32;cls.status=dll.open_cfw_bootloader_hw_interrupt_status_get_42c672_portable;cls.status.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(Instance)];cls.status.restype=ctypes.c_uint32;cls.clear=dll.open_cfw_bootloader_hw_interrupt_clear_42c6b6_portable;cls.clear.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(Instance)];cls.clear.restype=ctypes.c_uint32;cls.nvic_a=dll.open_cfw_bootloader_nvic_enable_bit_430240_portable;cls.nvic_a.argtypes=[ctypes.c_int16,ctypes.POINTER(ctypes.c_uint32)];cls.nvic_b=dll.open_cfw_bootloader_nvic_enable_bit_430470_portable;cls.nvic_b.argtypes=cls.nvic_a.argtypes;cls.priority=dll.open_cfw_bootloader_scb_priority_nibble_43025c_portable;cls.priority.argtypes=[ctypes.c_int16,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8)]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_status_route_and_error_precedence(self):
  value=ctypes.c_uint32((3<<1)|(5<<5));self.assertEqual(self.route(ctypes.byref(value),3),1);self.assertEqual(value.value,1);value.value=(3<<1)|(5<<5);self.assertEqual(self.route(ctypes.byref(value),5),1);self.assertEqual(value.value,16);self.assertEqual(self.route(ctypes.byref(value),7),0)
  self.assertEqual(self.classify(0x04,0),0x08000000);self.assertEqual(self.classify(1<<9,0),0x08000001);self.assertEqual(self.classify(1<<4,0),0x08000002);self.assertEqual(self.classify(0x0800,0),1);self.assertEqual(self.classify(0,0),0)
 def test_interrupt_validation_enable_status_and_clear(self):
  instance=Instance(0x20,0x35,0);valid=Handle(0x01123456,0);invalid=Handle(0,0);out=ctypes.c_uint32()
  self.assertEqual(self.enable(ctypes.byref(invalid),4,ctypes.byref(instance)),2);self.assertEqual(self.enable(ctypes.byref(valid),2,ctypes.byref(instance)),6);self.assertEqual(self.enable(ctypes.byref(valid),4,ctypes.byref(instance)),0);self.assertEqual(instance.control,0x24)
  self.assertEqual(self.status(ctypes.byref(valid),0,ctypes.byref(out),ctypes.byref(instance)),0);self.assertEqual(out.value,0x35);self.assertEqual(self.status(ctypes.byref(valid),1,ctypes.byref(out),ctypes.byref(instance)),0);self.assertEqual(out.value,0x24);self.assertEqual(self.status(ctypes.byref(valid),0,None,ctypes.byref(instance)),6);self.assertEqual(self.clear(ctypes.byref(valid),0x44,ctypes.byref(instance)),0);self.assertEqual(instance.clear,0x44)
 def test_nvic_and_priority_addressing(self):
  registers=(ctypes.c_uint32*3)();self.nvic_a(37,registers);self.assertEqual(registers[1],1<<5);self.nvic_b(65,registers);self.assertEqual(registers[2],2);snapshot=list(registers);self.nvic_a(-1,registers);self.assertEqual(list(registers),snapshot)
  external=(ctypes.c_uint8*64)();system=(ctypes.c_uint8*12)();self.priority(7,0x0B,external,system);self.assertEqual(external[7],0xB0);self.priority(-1,3,external,system);self.assertEqual(system[11],0x30);self.priority(-12,4,external,system);self.assertEqual(system[0],0x40)
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end in ITEMS:
     body,_=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=[],strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
