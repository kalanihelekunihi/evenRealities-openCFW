from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_thread_pointer_422874.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_thread_pointer_host.c"
class BootloaderThreadPointerTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();p=Path(c.tmp.name)/("tp.dylib" if sys.platform=="darwin" else "tp.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(p)],check=True,capture_output=True);c.fn=ctypes.CDLL(str(p)).open_cfw_bootloader_thread_pointer_422874;c.fn.restype=ctypes.c_size_t
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def test_authenticated_leaf_caller_and_successor(s):
  b=OFFICIAL.read_bytes();s.assertEqual(hashlib.sha256(b[0x12874:0x1287C]).hexdigest(),"15e4706dbe2a251bc34a133f37c69c8ac3b76df463aa23f70fc4415b9a96621b");s.assertEqual(b[0xED04:0xED08].hex(),"03f0b6fd");s.assertEqual(hashlib.sha256(b[0x1287C:0x12AAC]).hexdigest(),"76998e68a31e9f88c2e09a1c163b60f5b03f4d879dc135483c81f8b10edfe720")
 def test_returns_authenticated_runtime_anchor(s):s.assertEqual(s.fn(),0x20000518)
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-tp.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
