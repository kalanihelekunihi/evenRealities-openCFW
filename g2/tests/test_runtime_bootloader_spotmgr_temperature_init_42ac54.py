from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/bootloader/core_overlay/runtime_spotmgr_temperature_init_42ac54.c';BOOT=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';sys.path.insert(0,str(ROOT/'tools'));import apollo_overlay  # noqa:E402
ENABLE=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p);CONFIG=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_float,ctypes.c_void_p);WAIT=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/'t.dylib';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-Wall','-Wextra','-Werror','-dynamiclib',str(SOURCE),'-o',str(p)],check=True,capture_output=True,text=True);c.f=ctypes.CDLL(str(p)).open_cfw_bootloader_spotmgr_temperature_init_42ac54;c.f.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ENABLE,CONFIG,WAIT,ctypes.c_void_p];c.f.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def test_routes(self):
  for gate0,gate1,er,cr,wr,expected in ((1,0,0,0,0,1),(0,1,0,0,0,1),(0,0,1,0,0,1),(0,0,0,1,0,1),(0,0,0,0,1,4),(0,0,0,0,0,0)):
   calls=[]
   @ENABLE
   def en(v,_):calls.append(('e',v));return er
   @CONFIG
   def co(v,_):calls.append(('c',v));return cr
   @WAIT
   def wa(us,reg,_):calls.append(('w',us,reg));return wr
   self.assertEqual(self.f(gate0,gate1,en,co,wa,None),expected)
   if expected==0:self.assertEqual(calls,[('e',29),('c',-40.0),('w',2500,0x400083e0)])
 def test_exact(self):
  boot=BOOT.read_bytes();self.assertEqual(int.from_bytes(boot[0xd154:0xd158],'little'),0x42ac55)
  for cc,v in ((Path('/usr/bin/clang'),'Apple clang version 21.0.0'),(Path('/opt/homebrew/opt/llvm@22/bin/clang'),'Homebrew clang version 22.1.8')):
   if not cc.exists():self.skipTest(str(cc))
   self.assertTrue(subprocess.run([str(cc),'--version'],check=True,capture_output=True,text=True).stdout.startswith(v));o=Path(self.t.name)/(cc.parent.name+'.o');subprocess.run([str(cc),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never','-c',str(SOURCE),'-o',str(o)],check=True,capture_output=True,text=True);d,s=apollo_overlay.parse_elf32(o);q=apollo_overlay.section_named(s,'.text.open_cfw_bootloader_spotmgr_temperature_init_42ac54');b=bytearray(d[int(q['offset']):int(q['offset'])+int(q['size'])]);self.assertEqual(hashlib.sha256(b).hexdigest(),'3636b7608940cd6452c1a6127ea5f177682849cc3740f5c98f9a4483a4794450')
   for x,t in ((0x14,0x41bf84),(0x26,0x41ca2c),(0x38,0x41d21c)):b[x:x+4]=apollo_overlay.encode_thumb_bl(0x42ac54+x,t)
   self.assertEqual(bytes(b),boot[0x1ac54:0x1aca4])
if __name__=='__main__':unittest.main()
