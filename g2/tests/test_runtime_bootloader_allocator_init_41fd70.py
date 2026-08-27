from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';SOURCE=ROOT/'components/bootloader/core_overlay/runtime_allocator_init_41fd70.c';FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_allocator_init_host.c';BASE=0x410000;START=0x41FD70;END=0x41FDA8
def bl(b,a):
 o=a-BASE;f=int.from_bytes(b[o:o+2],'little');s=int.from_bytes(b[o+2:o+4],'little')
 if f&0xf800!=0xf000 or s&0xd000!=0xd000:return None
 sign=f>>10&1;i1=1^(s>>13&1)^sign;i2=1^(s>>11&1)^sign;v=(sign<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if v&1<<24:v-=1<<25
 return a+4+v
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();c.l=Path(c.t.name)/('x.dylib' if sys.platform=='darwin' else 'x.so');subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE),*(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC']),'-o',str(c.l)],check=True,capture_output=True,text=True);c.d=ctypes.CDLL(str(c.l))
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def test_stock_and_caller(self):
  b=OFFICIAL.read_bytes();self.assertEqual(hashlib.sha256(b[START-BASE:END-BASE]).hexdigest(),'e92241da4e692fb1acee34d31103f2aaf6439d88fd192b9ac0abf5f6785f2f2d');self.assertEqual(tuple(a for a in range(BASE,BASE+len(b)-3,2) if bl(b,a)==START),(0x41B89E,))
 def test_behavior(self):self.d.open_cfw_test_allocator_init.restype=ctypes.c_uint32;self.assertEqual(self.d.open_cfw_test_allocator_init(),1)
 def test_target(self):
  x=SOURCE.read_text();[self.assertIn(t,x) for t in ('0x20081000U','0x00070800U','0x2002718CU','0x00417241U')];o=Path(self.t.name)/'x.o';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(o)],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
