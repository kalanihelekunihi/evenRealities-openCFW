from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_constraint_memchr_422590.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_constraint_memchr_host.c"
class BootloaderConstraintMemchrTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();c.libpath=Path(c.tmp.name)/("constraint.dylib" if sys.platform=="darwin" else "constraint.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(c.libpath)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(c.libpath));c.dispatch=c.lib.open_cfw_bootloader_constraint_dispatch_422590;c.dispatch.argtypes=[ctypes.c_char_p];c.dispatch.restype=ctypes.c_uint32;c.memchr=c.lib.open_cfw_bootloader_memchr_4225d0;c.memchr.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32];c.memchr.restype=ctypes.c_void_p;c.lib.open_cfw_constraint_fixture_message.restype=ctypes.c_char_p;c.lib.open_cfw_constraint_fixture_pointer.restype=ctypes.c_size_t
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def u32(s,n):return ctypes.c_uint32.in_dll(s.lib,n)
 def setUp(s):s.lib.open_cfw_constraint_fixture_reset()
 def test_authenticated_bodies_pool_callers_and_shared_memchr(s):
  b=OFFICIAL.read_bytes();s.assertEqual(hashlib.sha256(b[0x12590:0x125AC]).hexdigest(),"0fb60f3cb36d88d77e7767e201951f1c239fe41b874b911a24b87b6e93b31e6c");s.assertEqual(hashlib.sha256(b[0x125AC:0x125D0]).hexdigest(),"6a1c3b3c218a63a0485994c42f851a99bff4fedd5443396ba4a7bbe7a1ba5b25");s.assertEqual(hashlib.sha256(b[0x125D0:0x12628]).hexdigest(),"ed4dd5b44329c11e723cdca6aa56a749fb62673c7839ca6da4dac59483a4be9b");s.assertEqual(b[0xE692:0xE696].hex(),"03f07dff");s.assertEqual(b[0xE7EA:0xE7EE].hex(),"03f0f1fe")
 def test_constraint_registered_and_default_paths(s):
  s.lib.open_cfw_constraint_fixture_install_handler();s.assertEqual(s.dispatch(b"bad range"),0x22);s.assertEqual(s.u32("open_cfw_constraint_fixture_handler_calls").value,1);s.assertEqual(s.lib.open_cfw_constraint_fixture_message(),b"bad range");s.assertEqual(s.u32("open_cfw_constraint_fixture_last_error").value,0x22);s.assertEqual(s.lib.open_cfw_constraint_fixture_pointer(),0)
  s.setUp();s.assertEqual(s.dispatch(None),0x22);s.assertEqual(s.u32("open_cfw_constraint_fixture_default_calls").value,1);s.assertEqual(s.lib.open_cfw_constraint_fixture_message(),b"constraint handler: bad message")
 def test_memchr_alignment_lengths_and_low_byte(s):
  raw=(ctypes.c_uint8*40)(*range(40));base=ctypes.addressof(raw)
  for off in range(4):
   for n in (0,1,3,7,8,9,31):
    needle=(off+n//2) if n else 99;expected=(base+needle if n and needle<off+n else 0);s.assertEqual(s.memchr(base+off,needle|0xAB00,n) or 0,expected)
  raw[29]=7;s.assertEqual(s.memchr(base+1,7,39),base+7)
 def test_memchr_absent_and_first_match(s):
  raw=(ctypes.c_uint8*16)(1,2,3,4,5,6,7,8,9,3,11,12,13,14,15,16);base=ctypes.addressof(raw);s.assertEqual(s.memchr(base,3,16),base+2);s.assertFalse(s.memchr(base,99,16));s.assertFalse(s.memchr(base,1,0))
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-constraint.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
