import ctypes, hashlib, random, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_clock_encode_42c26a.c"
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
A=0x42C26A;Z=0x42C3E2;BASE=0x410000;FN="open_cfw_bootloader_hw_clock_encode_42c26a"
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
SPECS=((0x12A,"open_cfw_bootloader_rounded_divider_42c222",0x42C222),(0x148,"open_cfw_bootloader_is_power_of_two_42c256",0x42C256),(0x15E,"open_cfw_bootloader_rounded_divider_42c222",0x42C222))
RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
def round_div(n,e,a,b,c):
 d=((a*2)+1)*(1<<(e-1))*((c*b)+1);return n//d+(n%d>d//2)
def reference(rate,select):
 if rate==0:return(0,0)
 ceiling=96000000//rate+(96000000%rate!=0);lowbit=(-ceiling)&ceiling;e=lowbit.bit_length()-1;e=min(e,6)
 special=int(rate<(96000000>>14)or 96000000//3<=rate<=(96000000//2)-1)
 scale=(special*2+1)*(1<<e);q=ceiling//scale+(ceiling%scale!=0);ql=q.bit_length()-1
 if ql>=8:e+=ql-7
 e+=1
 if e>=8:return(0,0)
 if ql>=8:
  scale=1<<(ql-7);q=q//scale+(q%scale!=0)
 exact=int(not(rate>=24000000 or (1<<(e-1))==ceiling));phase=(q-2)//2 if select==1 else(q-1)//2
 enc=((e<<8)&0xf00)|((special<<12)&0x1000)|((exact<<13)&0x2000)|((phase<<16)&0xff0000)|((q-1)<<24)
 actual=round_div(96000000,e,special,exact,q-1)
 if actual%250000==0 and actual//250000!=0 and actual//250000&(actual//250000-1)==0:
  actual=round_div(96000000,e,1,0,0);enc=((e<<8)&0xf00)|0x1000
 return enc&0xffffffff,actual
class HardwareClockEncodeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"clock.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);dll=ctypes.CDLL(str(lib));cls.encode=dll.open_cfw_bootloader_hw_clock_encode_42c26a_portable;cls.encode.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)];cls.encode.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def check(self,rate,select):
  actual=ctypes.c_uint32();observed=self.encode(rate,select,ctypes.byref(actual));self.assertEqual((observed,actual.value),reference(rate,select))
 def test_boundaries_and_fixed_rates(self):
  for rate in (0,1,5859,5860,5861,100000,1000000,23999999,24000000,31999999,32000000,40000000,47999999,48000000):
   self.check(rate,0);self.check(rate,1)
 def test_deterministic_differential(self):
  rng=random.Random(0x42C26A)
  for _ in range(10000):self.check(rng.randrange(0,48000001),rng.randrange(0,3))
 def test_null_actual_pointer(self):self.assertEqual(self.encode(400000,0,None),reference(400000,0)[0])
 def test_dual_toolchain_exact(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"23796b78366978bda2ee2db94e309c4f1cae4e92f5ffbc2072f75becca3ae9e8")
  with tempfile.TemporaryDirectory()as temp:
   for i,cc in enumerate(PROFILES):
    obj=Path(temp)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True);body,report=apollo_overlay.extract_in_place_function_section(obj,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(report["relocation_count"],3)
 def test_reviewable_source(self):
  text=SOURCE.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
