import ctypes,hashlib,importlib.util,itertools,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_state_decode_42b6b8.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42B6B8;Z=0x42B9BA;BASE=0x410000;MAIN_BASE=0x437FE0;MAIN_A=0x5A13E8;FN="open_cfw_bootloader_hw_state_decode_42b6b8";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
spec=importlib.util.spec_from_file_location("decode_integrator",ROOT/"tools/integrate_g2_bootloader_hw_state_decode_42b6b8.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
class Input(ctypes.Structure):_fields_=[("word0",ctypes.c_uint32),("word4",ctypes.c_uint32),("pad",ctypes.c_uint8*8),("field8",ctypes.c_uint8),("mode",ctypes.c_uint8),("kind",ctypes.c_uint8)]
P={0:(3,7),1:(11,15),16:(7,7),17:(15,15),256:(2,6),257:(10,14),272:(6,6),273:(14,14),512:(1,5),513:(9,13),528:(5,5),529:(13,13),768:(0,4),769:(8,12),784:(4,4),785:(12,12),0x100010:(19,19),0x100011:(15,15),0x100110:(18,18),0x100111:(14,14),0x100210:(17,17),0x100211:(13,13),0x100310:(16,16),0x100311:(12,12)}
S={0:(0,0),1:(1,7),0x1000:(2,2),0x1001:(4,4),0x2000:(3,3),0x2001:(5,5),0x10000:(6,6),0x10001:(7,7),0x11000:(2,2),0x11001:(4,4),0x12000:(3,3),0x12001:(5,5)}
def ref(i,dynamic,alternate):
 low=1 if i.mode==1 or(i.mode!=0 and dynamic&3==2)else 0;flag=1 if i.kind in(1,2)or((i.word0<<2)&0xffffffff)!=0 or i.word4&0x4c4 else 0;kind=2 if i.kind==2 else 1 if i.kind==1 else 0;hi=1 if ((i.word0<<2)&0xffffffff)!=0 or i.word4&0x4c4 else 0;top=1 if i.word0&0xc00000 else 0;state=(i.field8&15)<<8|low|flag<<4|kind<<12|hi<<16|top<<20
 if state&0xf00fff not in P:return(5,None,None)
 primary=P[state&0xf00fff][1 if alternate else 0]
 if state&0xff00f not in S:return(5,primary,None)
 return(0,primary,S[state&0xff00f][1 if alternate else 0])
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"decode.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.step=d.open_cfw_bootloader_hw_state_decode_42b6b8_portable;cls.step.argtypes=[ctypes.POINTER(Input),ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32)];cls.step.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_exhaustive_composed_classifications(self):
  cases=0
  for field8,mode,kind,word0,word4,dynamic,alt in itertools.product(range(16),range(4),range(4),(0,1,0x400000,0x800000),(0,0x4,0x40,0x400),(0,2),(0,1)):
   i=Input(word0=word0,word4=word4,field8=field8,mode=mode,kind=kind);p=ctypes.c_uint32(0xdeadbeef);s=ctypes.c_uint32(0xcafebabe);want=ref(i,dynamic,alt);got=self.step(ctypes.byref(i),0xa5a5a5a5,dynamic,alt,ctypes.byref(p),ctypes.byref(s));self.assertEqual(got,want[0]);self.assertEqual(p.value,0xdeadbeef if want[1]is None else want[1]);self.assertEqual(s.value,0xcafebabe if want[2]is None else want[2]);cases+=1
  self.assertEqual(cases,16384)
 def test_null_guards(self):self.assertEqual(self.step(None,0,0,0,None,None),0xffffffff)
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),mod.BH);analogue=MAIN.read_bytes()[MAIN_A-MAIN_BASE:MAIN_A-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),738)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=[],strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual((r["relocation_count"],r["unrelocated_sha256"]),(0,mod.UH))
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
