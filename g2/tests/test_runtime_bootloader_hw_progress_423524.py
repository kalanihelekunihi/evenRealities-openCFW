from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_progress_423524.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_hw_progress_host.c"
class Instance(ctypes.Structure):_fields_=[("bytes",ctypes.c_uint8*0x11c)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();o=Path(c.tmp.name)/("hwp.dylib" if sys.platform=="darwin" else "hwp.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"]if sys.platform=="darwin"else["-shared","-fPIC"]),"-o",str(o)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(o));c.primary=c.lib.open_cfw_bootloader_hw_primary_progress_423524;c.secondary=c.lib.open_cfw_bootloader_hw_secondary_progress_423608
  for f in(c.primary,c.secondary):f.argtypes=[ctypes.POINTER(Instance)];f.restype=None
  for n in("token","enter_count","restore_count","restored_token","primary_result","primary_count","primary_requested","secondary_result","secondary_count","secondary_requested","primary_callback_count","primary_callback_event","secondary_callback_count","secondary_callback_event","pump_count","snapshot_count"):setattr(c,n,ctypes.c_uint32.in_dll(c.lib,"open_cfw_hwp_host_"+n))
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def setUp(s):
  for n in("enter_count","restore_count","restored_token","primary_result","primary_count","primary_requested","secondary_result","secondary_count","secondary_requested","primary_callback_count","primary_callback_event","secondary_callback_count","secondary_callback_event","pump_count","snapshot_count"):getattr(s,n).value=0
  s.token.value=0xa55a5aa5;s.i=Instance()
 def w(s,o,v):
  for k in range(4):s.i.bytes[o+k]=(v>>(8*k))&255
 def r(s,o):return sum(int(s.i.bytes[o+k])<<(8*k) for k in range(4))
 def test_stock_bodies(s):
  b=OFFICIAL.read_bytes();s.assertEqual(hashlib.sha256(b[0x13524:0x13608]).hexdigest(),"be77b63cd268da7b27fcb99a8046654e1e527ed65c8118430e7d540bc0fe46c7");s.assertEqual(hashlib.sha256(b[0x13608:0x136ce]).hexdigest(),"0c57e8cf946a5c825784001ef88eb8e0a9c94dc820a29b0e9ed9636aebb7996d")
 def test_primary_progress_completion_mirror_callback_and_pump(s):
        s.i.bytes[0x119]=s.i.bytes[0xdc]=1;s.w(0xd8,3);s.w(0xa4,8);s.w(0xa8,1);s.w(0xb0,1);s.primary_result.value=1;s.primary_count.value=5;s.primary(ctypes.byref(s.i));s.assertEqual((s.primary_requested.value,s.r(0xd8),s.r(0xac)),(5,8,8));s.assertEqual((s.i.bytes[0x119],s.primary_callback_count.value,s.primary_callback_event.value,s.pump_count.value),(0,1,0,1));s.assertEqual((s.enter_count.value,s.restore_count.value,s.restored_token.value),(1,1,s.token.value))
 def test_primary_descriptor_empty_aborts_without_progress_or_pump(s):
  s.i.bytes[0x119]=s.i.bytes[0xdc]=1;s.w(0xd8,2);s.w(0xa4,9);s.w(0xb0,1);s.primary_result.value=0;s.primary(ctypes.byref(s.i));s.assertEqual((s.r(0xd8),s.i.bytes[0x119],s.primary_callback_event.value,s.pump_count.value),(2,0,1,0))
 def test_secondary_snapshot_progress_completion_and_callback(s):
  s.i.bytes[0x11a]=s.i.bytes[0xdd]=1;s.w(0x9c,4);s.w(0x68,10);s.w(0x6c,1);s.w(0x74,1);s.secondary_result.value=1;s.secondary_count.value=6;s.secondary(ctypes.byref(s.i));s.assertEqual((s.snapshot_count.value,s.secondary_requested.value,s.r(0x9c),s.r(0x70)),(1,6,10,10));s.assertEqual((s.i.bytes[0x11a],s.secondary_callback_event.value),(0,0))
 def test_secondary_descriptor_empty_aborts(s):
  s.i.bytes[0x11a]=s.i.bytes[0xdd]=1;s.w(0x9c,1);s.w(0x68,5);s.w(0x74,1);s.secondary_result.value=0;s.secondary(ctypes.byref(s.i));s.assertEqual((s.r(0x9c),s.i.bytes[0x11a],s.secondary_callback_event.value),(1,0,1))
 def test_source_cross_compiles(s):
  for c in("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(c).exists():subprocess.run([c,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(c).parent.name+"-hwp.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
