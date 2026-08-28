from __future__ import annotations
import ctypes,hashlib,os,random,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_u64_divmod_42287c.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_u64_divmod_host.c"
class BootloaderU64DivmodTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();p=Path(c.tmp.name)/("div.dylib" if sys.platform=="darwin" else "div.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(p)],check=True,capture_output=True);c.fn=ctypes.CDLL(str(p)).open_cfw_bootloader_u64_divmod_42287c;c.fn.argtypes=[ctypes.c_uint64,ctypes.c_uint64,ctypes.POINTER(ctypes.c_uint64)];c.fn.restype=ctypes.c_uint64
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def check(s,a,b):r=ctypes.c_uint64();q=s.fn(a,b,ctypes.byref(r));s.assertEqual((q,r.value),(a//b,a%b))
 def test_authenticated_body_callers_tail_and_successor(s):
  b=OFFICIAL.read_bytes();s.assertEqual(hashlib.sha256(b[0x1287C:0x12AAC]).hexdigest(),"76998e68a31e9f88c2e09a1c163b60f5b03f4d879dc135483c81f8b10edfe720");s.assertEqual(hashlib.sha256(b[0x12AAC:0x12AC8]).hexdigest(),"7d5250344a7e889515915c327cf7a10ce0a248a7be5b86784de3f5f3633542cd");s.assertEqual([b[x-0x410000:x-0x410000+4].hex() for x in (0x41F1D0,0x41F1EA,0x422E74)],["03f054fb","03f047fb","fff702fd"]);s.assertEqual(b[0x128E0:0x128E4].hex(),"04f082be")
 def test_small_and_power_of_two_divisors(s):
  for a in (0,1,2,3,0xffffffff,0x100000000,0xffffffffffffffff):
   for b in (1,2,3,0xffff,0x10000):s.check(a,b)
 def test_high_word_and_normalization_paths(s):
  cases=((0xffffffffffffffff,0x100000001),(0xdeadbeefcafebabe,0x100000000),(0x8000000000000000,0x1000000),(0x123456789abcdef0,0x12345678),(0x123456789abcdef0,0x1000000000000000))
  for a,b in cases:s.check(a,b)
 def test_deterministic_differential_samples(s):
  rng=random.Random(0x42287C)
  for _ in range(500):a=rng.getrandbits(64);b=rng.getrandbits(64) or 1;s.check(a,b)
 def test_divide_by_zero_host_contract_and_cross_compile(s):
  r=ctypes.c_uint64();s.assertEqual(s.fn(0x123456789ABCDEF0,0,ctypes.byref(r)),0);s.assertEqual(r.value,0x123456789ABCDEF0)
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-div.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
