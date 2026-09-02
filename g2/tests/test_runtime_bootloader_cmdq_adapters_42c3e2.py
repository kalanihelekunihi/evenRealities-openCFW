import ctypes
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_cmdq_adapters_42c3e2.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";BASE=0x410000
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_cmdq_adapter_init_42c3e2",0x42C3E2,0x42C420,0x2C,"open_cfw_bootloader_cmdq_init_427794",0x427794),("open_cfw_bootloader_cmdq_adapter_enable_42c420",0x42C420,0x42C44E,0x28,"open_cfw_bootloader_cmdq_enable_427878",0x427878),("open_cfw_bootloader_cmdq_adapter_disable_42c44e",0x42C44E,0x42C45A,0x06,"open_cfw_bootloader_cmdq_disable_4278c8",0x4278C8))
class Config(ctypes.Structure):_fields_=[("capacity",ctypes.c_uint32),("descriptor",ctypes.c_uint32),("priority",ctypes.c_uint8)]
class State(ctypes.Structure):_fields_=[("queue_handle",ctypes.c_uint32),("active",ctypes.c_uint32),("auxiliary",ctypes.c_uint32),("link",ctypes.POINTER(ctypes.c_uint32))]
INIT=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint8,ctypes.POINTER(Config),ctypes.POINTER(ctypes.c_uint32));CONTROL=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32)
class CmdqAdapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"cmdqa.so";cc=shutil.which("cc") or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.initialize=dll.open_cfw_bootloader_cmdq_adapter_init_42c3e2_portable;cls.initialize.argtypes=[ctypes.POINTER(State),ctypes.c_uint8,ctypes.c_uint32,ctypes.c_uint32,INIT];cls.initialize.restype=ctypes.c_uint32;cls.enable=dll.open_cfw_bootloader_cmdq_adapter_enable_42c420_portable;cls.enable.argtypes=[ctypes.POINTER(State),ctypes.POINTER(ctypes.c_uint32),CONTROL];cls.enable.restype=ctypes.c_uint32;cls.disable=dll.open_cfw_bootloader_cmdq_adapter_disable_42c44e_portable;cls.disable.argtypes=[ctypes.POINTER(State),CONTROL];cls.disable.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_initialize_contract_and_failure(self):
  seen=[]
  @INIT
  def success(instance,config,handle):seen.append((instance,config.contents.capacity,config.contents.descriptor,config.contents.priority));handle[0]=0x55;return 0
  state=State(9,9,9,None);self.assertEqual(self.initialize(ctypes.byref(state),3,200,0x1234,success),0);self.assertEqual(seen,[(3,100,0x1234,1)]);self.assertEqual((state.queue_handle,state.active,state.auxiliary),(0x55,0x100,0))
  @INIT
  def failure(_instance,_config,_handle):return 6
  self.assertEqual(self.initialize(ctypes.byref(state),1,8,0,failure),6);self.assertEqual(state.active,0)
 def test_enable_disable_and_link_initialization(self):
  calls=[]
  @CONTROL
  def control(handle):calls.append(handle);return handle+1
  state=State(0x41,0,0,None);links=(ctypes.c_uint32*2)();self.assertEqual(self.enable(ctypes.byref(state),links,control),0x42);self.assertEqual(links[0],ctypes.addressof(links)&0xffffffff);self.assertEqual(links[1],links[0]);links[0]=7;self.assertEqual(self.enable(ctypes.byref(state),links,control),0x42);self.assertEqual(links[0],7);self.assertEqual(self.disable(ctypes.byref(state),control),0x42);self.assertEqual(calls,[0x41,0x41,0x41])
 def test_dual_toolchain_exact(self):
  boot=BOOT.read_bytes()
  with tempfile.TemporaryDirectory() as temp:
   for profile,compiler in enumerate(PROFILES):
    obj=Path(temp)/f"{profile}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True)
    for name,start,end,offset,symbol,target in ITEMS:
     relocs=[{"offset":offset,"type":"R_ARM_THM_CALL","symbol":symbol,"symbol_type":"STT_NOTYPE","target_address":target}];body,_=apollo_overlay.extract_in_place_function_section(obj,name,runtime_address=start,relocation_configs=relocs,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,boot[start-BASE:end-BASE])
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
