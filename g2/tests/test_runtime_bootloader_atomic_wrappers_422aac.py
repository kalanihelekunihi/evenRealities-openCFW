from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_atomic_wrappers_422aac.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_atomic_wrappers_host.c"
class BootloaderAtomicWrapperTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();p=Path(c.tmp.name)/("atomic.dylib" if sys.platform=="darwin" else "atomic.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(p)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(p));c.snap=c.lib.open_cfw_bootloader_atomic_snapshot3_422aac;c.snap.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32)];c.query=c.lib.open_cfw_bootloader_retained_query_wrapper_422aca;c.query.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def test_authenticated_bodies_caller_provider_and_alignment(s):
  b=OFFICIAL.read_bytes();pins=((0x12AAC,0x12AC8,"7d5250344a7e889515915c327cf7a10ce0a248a7be5b86784de3f5f3633542cd"),(0x12AC8,0x12ACA,"c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),(0x12ACA,0x12AD2,"71476a7b2f4e36a5351aca1a4b62c5cbe7f99c4d657bdb42e8932fd47d0041ad"));
  for a,z,h in pins:s.assertEqual(hashlib.sha256(b[a:z]).hexdigest(),h)
  s.assertEqual(b[0xF42A:0xF42E].hex(),"03f03ffb");s.assertEqual(b[0x12ACC:0x12AD0].hex(),"faf774f9");s.assertEqual(b[0x12AD2:0x12AD4],b"\0\0")
 def test_snapshot_noop_and_retained_query(s):
  src=ctypes.c_uint32(0xA5A55A5A);dst=(ctypes.c_uint32*3)();s.snap(ctypes.byref(src),dst);s.assertEqual(list(dst),[src.value]*3);s.lib.open_cfw_bootloader_noop_422ac8();ctypes.c_uint32.in_dll(s.lib,"open_cfw_atomic_host_query_value").value=0x12345678;s.assertEqual(s.query(),0x12345678);s.assertEqual(ctypes.c_uint32.in_dll(s.lib,"open_cfw_atomic_host_query_calls").value,1)
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-atomic.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
