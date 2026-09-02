from __future__ import annotations
import ctypes,hashlib,math,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'components/bootloader/core_overlay/runtime_spotmgr_temperature_range_42ad40.c';B=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';sys.path.insert(0,str(ROOT/'tools'));import apollo_overlay  # noqa:E402
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/'r.dylib';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-Wall','-Wextra','-Werror','-dynamiclib',str(S),'-o',str(p)],check=True,capture_output=True,text=True);c.f=ctypes.CDLL(str(p)).open_cfw_bootloader_spotmgr_temperature_range_42ad40;c.f.argtypes=[ctypes.c_float];c.f.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def test_boundaries_and_non_finite(self):
  for v,e in [(-math.inf,4),(-274,4),(-273,0),(-20.0001,0),(-20,1),(-0.1,1),(0,2),(49.999,2),(50,3),(999.9,3),(1000,4),(math.inf,4),(math.nan,4)]:self.assertEqual(self.f(v),e)
 def test_exact_dual(self):
  stock=B.read_bytes()[0x1ad40:0x1adb8]
  for cc,v in ((Path('/usr/bin/clang'),'Apple clang version 21.0.0'),(Path('/opt/homebrew/opt/llvm@22/bin/clang'),'Homebrew clang version 22.1.8')):
   if not cc.exists():self.skipTest(str(cc))
   self.assertTrue(subprocess.run([str(cc),'--version'],check=True,capture_output=True,text=True).stdout.startswith(v));o=Path(self.t.name)/(cc.parent.name+'.o');subprocess.run([str(cc),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never','-c',str(S),'-o',str(o)],check=True,capture_output=True,text=True);d,s=apollo_overlay.parse_elf32(o);q=apollo_overlay.section_named(s,'.text.open_cfw_bootloader_spotmgr_temperature_range_42ad40');body=d[int(q['offset']):int(q['offset'])+int(q['size'])];self.assertEqual(body,stock);self.assertEqual(hashlib.sha256(body).hexdigest(),'89f71050cf7850205a7a5ef9ccfb09dfadaadd5a6046355844d800589b65607d')
if __name__=='__main__':unittest.main()
