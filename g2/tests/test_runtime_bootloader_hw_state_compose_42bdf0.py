import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_state_compose_42bdf0.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42BDF0;Z=0x42BF4E;BASE=0x410000;MAIN_BASE=0x437FE0;FN="open_cfw_bootloader_hw_state_compose_42bdf0";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x3A,"open_cfw_bootloader_config_read_421548",0x421548),(0x96,"open_cfw_bootloader_config_read_421548",0x421548),(0xB8,"open_cfw_bootloader_config_read_421548",0x421548),(0x154,"open_cfw_bootloader_hw_state_commit_41cc04",0x41CC04));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("gate_control",ctypes.c_uint32),("gate_status",ctypes.c_uint32),("read_status",ctypes.c_uint32*3),("primary",ctypes.c_uint32*16),("secondary",ctypes.c_uint32*4),("tertiary",ctypes.c_uint32),("state",ctypes.c_uint32*27),("commit_calls",ctypes.c_uint32)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"compose.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.compose=d.open_cfw_bootloader_hw_state_compose_42bdf0_portable;cls.compose.argtypes=[ctypes.POINTER(Model)];cls.compose.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_gate_and_provider_failures(self):
  s=Model();s.gate_control=8;self.assertEqual(self.compose(ctypes.byref(s)),7)
  for i,status in enumerate((3,4,5)):
   s=Model();s.read_status[i]=status;self.assertEqual(self.compose(ctypes.byref(s)),status);self.assertEqual(s.commit_calls,0)
 def test_successful_copy_and_packed_composition(self):
  s=Model()
  for i in range(16):s.primary[i]=(i+1)*0x01010101
  for i in range(4):s.secondary[i]=0xA0+i
  s.tertiary=0xFFFFFFFF;self.assertEqual(self.compose(ctypes.byref(s)),0);self.assertEqual((s.state[0],s.commit_calls),(0x1F01600D,1));self.assertEqual(list(s.state[21:25]),[0xA0,0xA1,0xA2,0xA3]);self.assertEqual((s.state[26]>>20)&63,31)
  for i in range(4):self.assertEqual(s.state[17+i]&127,s.state[13+i]&127)
  a=(s.primary[12]>>21)&127;b=(s.primary[13]>>21)&127;self.assertEqual((s.state[9]>>21)&127,(a+b)//2)
 def test_gate_allows_when_status_bit_is_set(self):
  s=Model();s.gate_control=8;s.gate_status=1<<27;self.assertEqual(self.compose(ctypes.byref(s)),0)
 def test_invalid_model(self):self.assertEqual(self.compose(None),0xFFFFFFFF)
 def test_dual_toolchain_exact_and_stored_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"6abb107b7aebe13eaff37f34185f8865b71f27c756f8214d3646efa4f2304c1c");self.assertEqual(int.from_bytes(BOOT.read_bytes()[0x41D164-BASE:0x41D168-BASE],"little"),A|1);analogue=MAIN.read_bytes()[0x5A1C18-MAIN_BASE:0x5A1C18-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),313)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],4);self.assertEqual(r["unrelocated_sha256"],"b58f55d554bf0421fd534e60ce347afec006da6d395801821ed11dbe26ff5f41")
 def test_reviewable(self):
  text=SOURCE.read_text()
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
