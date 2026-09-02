import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_late_wrappers_42fff2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_mode_one_apply_42fff2",0x42FFF2,0x42FFFE,((0x06,"open_cfw_bootloader_mode_apply_42ff00",0x42FF00),)),("open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC,0x4303DE,((0x10,"open_cfw_bootloader_boolean_route_41d9aa",0x41D9AA),)),("open_cfw_bootloader_validated_byte_copy_430a9c",0x430A9C,0x430AC4,((0x0C,"open_cfw_bootloader_address_validate_430a60",0x430A60),(0x1A,"open_cfw_bootloader_byte_copy_41568c",0x41568C))),("open_cfw_bootloader_validated_word_transfer_430ac4",0x430AC4,0x430AEC,((0x0C,"open_cfw_bootloader_address_validate_430a60",0x430A60),(0x1A,"open_cfw_bootloader_word_transfer_provider_430b10",0x430B10))),("open_cfw_bootloader_word_transfer_critical_430b10",0x430B10,0x430B3C,((0x12,"open_cfw_bootloader_critical_save_41b8ec",0x41B8EC),(0x20,"open_cfw_bootloader_alignment_dispatch_42e4f4",0x42E4F4))),("open_cfw_bootloader_platform_services_init_43194c",0x43194C,0x43198A,((0x02,"open_cfw_bootloader_platform_init_41733c",0x41733C),(0x0A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x12,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x1A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x22,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x2A,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x32,"open_cfw_bootloader_platform_route_4174a6",0x4174A6),(0x36,"open_cfw_bootloader_platform_finish_417392",0x417392))))
PAIR=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32);ROUTE=ctypes.CFUNCTYPE(None,ctypes.c_uint32,ctypes.c_uint32);VOID=ctypes.CFUNCTYPE(None)
class LateWrapperTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"late.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.mode=dll.open_cfw_bootloader_mode_one_apply_42fff2_portable;cls.mode.argtypes=[ROUTE];cls.boolean=dll.open_cfw_bootloader_boolean_route_status_4303bc_portable;cls.boolean.argtypes=[ctypes.c_uint32,ctypes.c_uint32,PAIR];cls.boolean.restype=ctypes.c_uint32;cls.critical=dll.open_cfw_bootloader_word_transfer_critical_430b10_portable;cls.critical.argtypes=[ctypes.c_uint32,PAIR];cls.critical.restype=ctypes.c_uint32;cls.platform=dll.open_cfw_bootloader_platform_services_init_43194c_portable;cls.platform.argtypes=[VOID,ROUTE,VOID];cls.platform.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_mode_boolean_and_word_count(self):
  seen=[]
  @ROUTE
  def route(a,b):seen.append((a,b))
  @PAIR
  def pair(a,b):seen.append((a,b));return a^b
  self.mode(route);self.assertEqual(self.boolean(1,1,pair),0);self.assertEqual(self.boolean(1,7,pair),0xffffffff);self.assertEqual(self.critical(9,pair),3^0x12344321);self.assertEqual(seen[:3],[(1,1),(1,1),(1,0)])
 def test_platform_route_sequence(self):
  seen=[]
  @VOID
  def initialize():seen.append(("init",))
  @ROUTE
  def route(a,b):seen.append((a,b))
  @VOID
  def finish():seen.append(("finish",))
  self.assertEqual(self.platform(initialize,route,finish),0);self.assertEqual(seen,[('init',),(0,0xff),(1,0xd7),(2,0xd7),(3,0xd7),(4,0xd7),(5,0xd7),('finish',)])
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,specs in ITEMS:
     relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target} for offset,symbol,target in specs];body,_=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
