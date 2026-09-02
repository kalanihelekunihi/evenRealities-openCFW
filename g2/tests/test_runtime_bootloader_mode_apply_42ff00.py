import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mode_apply_42ff00.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";A=0x42FF00;Z=0x42FFF2;BASE=0x410000;FN="open_cfw_bootloader_mode_apply_42ff00";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x3C,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x52,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x68,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x7E,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0x84,"open_cfw_bootloader_critical_enter_41b8ec",0x41B8EC),(0xC4,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0xCE,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC),(0xEA,"open_cfw_bootloader_boolean_route_status_4303bc",0x4303BC));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
Route=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"mode.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.apply=d.open_cfw_bootloader_mode_apply_42ff00_portable;cls.apply.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),Route]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def invoke(self,mode,value,bits=0):
  seen=[]
  @Route
  def route(service,enabled):seen.append((service,enabled));return 0
  state=ctypes.c_uint32(bits);self.apply(mode,value,ctypes.byref(state),route);return state.value,seen
 def test_direct_mode_routes_and_boolean_normalization(self):
  for mode,service in ((1,0x81),(2,0x7D),(3,0x80),(4,0x8E),(8,0x92)):
   self.assertEqual(self.invoke(mode,1)[1],[(service,1)]);self.assertEqual(self.invoke(mode,2)[1],[(service,0)]);self.assertEqual(self.invoke(mode|0x100,1)[1],[(service,1)])
 def test_aggregate_modes_set_clear_and_publish(self):
  state,seen=self.invoke(6,1);self.assertEqual(state,1<<6);self.assertEqual(seen,[(0x86,1)])
  state,seen=self.invoke(7,1,state);self.assertEqual(state,(1<<6)|(1<<7));self.assertEqual(seen,[(0x86,1)])
  state,seen=self.invoke(6,0,state);self.assertEqual(state,1<<7);self.assertEqual(seen,[(0x86,1)])
  state,seen=self.invoke(7,0,state);self.assertEqual(state,0);self.assertEqual(seen,[(0x86,0)])
  state,seen=self.invoke(9,2,state);self.assertEqual(state,0);self.assertEqual(seen,[(0x86,0)])
 def test_unknown_mode_is_noop(self):self.assertEqual(self.invoke(5,1),(0,[]));self.assertEqual(self.invoke(0,1),(0,[]))
 def test_dual_toolchain_exact_and_shared_state_literal(self):
  image=BOOT.read_bytes();stock=image[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"2bf23ab0e4988009a2692db968a818ffeb5f010919982b1235db1b85d8735ae6");self.assertEqual(int.from_bytes(image[0x430204-BASE:0x430208-BASE],"little"),0x200270D0)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],8);self.assertEqual(r["unrelocated_sha256"],"3f26b603da390864dd2be07c458566263a63400f78d428f98113b1540bc53d1d")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
