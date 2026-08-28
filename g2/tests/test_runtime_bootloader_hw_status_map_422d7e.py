from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_status_map_422d7e.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_hw_status_map_host.c"
class BootloaderHardwareStatusMapTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();p=Path(c.tmp.name)/("hw-status.dylib" if sys.platform=="darwin" else "hw-status.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(p)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(p));c.map=c.lib.open_cfw_bootloader_hw_status_map_422d7e;c.map.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32];c.map.restype=ctypes.c_uint32;c.regs=((ctypes.c_uint32*32)*4).in_dll(c.lib,"open_cfw_hwsm_host_registers")
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def test_authenticated_body_literals_data_and_successor(s):
  b=OFFICIAL.read_bytes();s.assertEqual(hashlib.sha256(b[0x12D7E:0x12DC6]).hexdigest(),"87a7c4d6609c8566af29c21281d2746ac1af8dc81b95867b99defa5fd6e64261");s.assertEqual(b[0x12D7A:0x12D7E],(0x20000002).to_bytes(4,"little"));s.assertEqual(tuple(int.from_bytes(b[o:o+4],"little") for o in (0x13768,0x1376C,0x13770,0x13774,0x13778,0x1382C)),tuple(0x08000006+i for i in range(6)));s.assertEqual(b[0x12DC6:0x12DCA].hex(),"38b51c00")
 def test_fallback_and_each_mapped_bit_from_argument_or_register(s):
  for index in range(4):
   for row,bit in enumerate((6,7,8,9,10,12)):
    s.regs[index][15]=0;s.assertEqual(s.map(0xDEADBEEF,1<<bit,index),0x08000006+row);s.regs[index][15]=1<<bit;s.assertEqual(s.map(0xDEADBEEF,0,index),0x08000006+row)
   s.regs[index][15]=0;s.assertEqual(s.map(0xDEADBEEF,0,index),0xDEADBEEF)
 def test_priority_is_lowest_authenticated_bit(s):
  s.regs[2][15]=(1<<12)|(1<<9);s.assertEqual(s.map(3,(1<<10)|(1<<7),2),0x08000007)
 def test_unrelated_bits_preserve_fallback(s):
  s.regs[1][15]=0xffffffff&~sum(1<<b for b in (6,7,8,9,10,12));s.assertEqual(s.map(0x12345678,0,1),0x12345678)
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-hw-status.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
