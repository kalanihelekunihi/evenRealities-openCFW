from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_debug_services_422468.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_debug_services_host.c"
class BootloaderDebugServiceTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();c.libpath=Path(c.tmp.name)/("debug.dylib" if sys.platform=="darwin" else "debug.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(c.libpath)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(c.libpath));c.disable=c.lib.open_cfw_bootloader_debug_disable_422468;c.power=c.lib.open_cfw_bootloader_debug_power_4224b2;c.trace=c.lib.open_cfw_bootloader_debug_trace_disable_42252e;c.disable.restype=c.trace.restype=ctypes.c_uint32;c.power.argtypes=[ctypes.c_uint32];c.power.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def u8(s,n):return ctypes.c_uint8.in_dll(s.lib,n)
 def u32(s,n):return ctypes.c_uint32.in_dll(s.lib,n)
 def setUp(s):s.lib.open_cfw_debug_fixture_reset()
 def test_authenticated_bodies_pool_and_callers(s):
  b=OFFICIAL.read_bytes();spans=((0x12468,0x124B2,"9814e1b60b7637ccba467334aa7b21c00499c3cf7cae113298c14382895a128c"),(0x124B2,0x1252E,"b7b01e46563d81bfb3fc99e96b55564bde5536b1fc5fa05f181d968b66b3d6c1"),(0x1252E,0x12574,"61f149cf2cde2cd012ae5681429719effeefa99fd267a9231880ba21d3253bdc"));
  for a,z,h in spans:s.assertEqual(hashlib.sha256(b[a:z]).hexdigest(),h)
  s.assertEqual(hashlib.sha256(b[0x12574:0x12590]).hexdigest(),"82d8e4094be3bec9b384ed5df514b62e04f9af0b28bc15b7c1e00ef79613d62e")
  s.assertEqual(b[0x13D4C:0x13D50].hex(),"fef78cfb");s.assertEqual(b[0x13DF6:0x13DFA].hex(),"fef737fb")
 def test_power_tracks_initial_domain_and_reference_count(s):
  s.assertEqual(s.power(1),0);s.assertEqual(s.u8("open_cfw_debug_host_power_count").value,1);s.assertEqual(s.u8("open_cfw_debug_host_power_entry_state").value,1);s.assertEqual(s.u32("open_cfw_debug_host_enable_calls").value,1);s.assertEqual(s.u32("open_cfw_debug_host_last_device").value,28)
  s.assertEqual(s.power(1),0);s.assertEqual(s.u32("open_cfw_debug_host_query_calls").value,1);s.assertEqual(s.power(0),3);s.assertEqual(s.power(0),0);s.assertEqual(s.u32("open_cfw_debug_host_disable_calls").value,1)
  s.setUp();s.u32("open_cfw_debug_host_power_was_enabled").value=1;s.assertEqual(s.power(1),0);s.assertEqual(s.u8("open_cfw_debug_host_power_entry_state").value,3);s.assertEqual(s.power(0),0);s.assertEqual(s.u32("open_cfw_debug_host_disable_calls").value,0)
 def test_trace_disable_reference_count_register_and_poll(s):
  s.u8("open_cfw_debug_host_trace_count").value=2;s.u32("open_cfw_debug_host_demcr").value=0xFFFFFFFF;s.assertEqual(s.trace(),3);s.assertEqual(s.u32("open_cfw_debug_host_delay_calls").value,0)
  s.u32("open_cfw_debug_host_delay_result").value=9;s.assertEqual(s.trace(),9);s.assertEqual(s.u32("open_cfw_debug_host_demcr").value,0xFEFFFFFF);s.assertEqual((s.u32("open_cfw_debug_host_last_timeout").value,s.u32("open_cfw_debug_host_last_mask").value,s.u32("open_cfw_debug_host_last_value").value),(10,0x01000000,0))
 def test_debug_disable_clears_clock_and_releases_services(s):
  s.u8("open_cfw_debug_host_enable_count").value=1;s.u8("open_cfw_debug_host_trace_count").value=1;s.u8("open_cfw_debug_host_power_count").value=1;s.u8("open_cfw_debug_host_power_entry_state").value=1;s.u32("open_cfw_debug_host_dbgctrl").value=0xFFFFFFFF;s.u32("open_cfw_debug_host_demcr").value=0xFFFFFFFF;s.assertEqual(s.disable(),0);s.assertEqual(s.u32("open_cfw_debug_host_dbgctrl").value,0xFFFFFFF0);s.assertEqual(s.u32("open_cfw_debug_host_demcr").value,0xFEFFFFFF);s.assertEqual(s.u32("open_cfw_debug_host_disable_calls").value,1);s.assertEqual(s.u32("open_cfw_debug_host_restore_calls").value,3)
  s.setUp();s.u8("open_cfw_debug_host_enable_count").value=2;s.u8("open_cfw_debug_host_trace_count").value=2;s.u8("open_cfw_debug_host_power_count").value=2;s.u32("open_cfw_debug_host_dbgctrl").value=0xF;s.assertEqual(s.disable(),3);s.assertEqual(s.u32("open_cfw_debug_host_dbgctrl").value,0xF)
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-debug.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
