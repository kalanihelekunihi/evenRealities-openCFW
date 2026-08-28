from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';S=R/'components/bootloader/core_overlay/runtime_mspi_control_41fe28.c';F=R/'tests/fixtures/bootloader_runtime_mspi_control_host.c';BASE=0x410000
def bl(b,a):
 o=a-BASE;f=int.from_bytes(b[o:o+2],'little');s=int.from_bytes(b[o+2:o+4],'little')
 if f&0xf800!=0xf000 or s&0xd000!=0xd000:return None
 q=f>>10&1;i1=1^(s>>13&1)^q;i2=1^(s>>11&1)^q;v=(q<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if v&1<<24:v-=1<<25
 return a+4+v
class T(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();c.p=Path(c.t.name)/('x.dylib' if sys.platform=='darwin' else 'x.so');subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(F),*(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC']),'-o',str(c.p)],check=True);c.d=ctypes.CDLL(str(c.p));c.d.open_cfw_mspi_fixture_call.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def calls(self):return [self.d.open_cfw_mspi_fixture_call(i) for i in range(self.d.open_cfw_mspi_fixture_count())]
 def test_stock(self):
  b=B.read_bytes();self.assertEqual(hashlib.sha256(b[0xfe28:0xfe48]).hexdigest(),'e192108a57e6cd824fb7b17e9e1fa3d39dd77e8dbea29cd967959f433f05a7f7');self.assertEqual(hashlib.sha256(b[0xfe48:0xfe62]).hexdigest(),'d72aa87850dfc17bee8c0668d9286d189027b2ef9bf7f3a7727f243bef10f518');self.assertEqual(tuple(a for a in range(BASE,BASE+len(b)-3,2) if bl(b,a)==0x41fe28),(0x41ff2a,0x420520));self.assertEqual(tuple(a for a in range(BASE,BASE+len(b)-3,2) if bl(b,a)==0x41fe48),(0x41ff18,))
  self.assertEqual(int.from_bytes(b[0x10874:0x10878],'little'),0x200270dc);self.assertEqual(int.from_bytes(b[0x10878:0x1087c],'little'),0x200271c6)
 def test_behavior(self):
  self.d.open_cfw_mspi_fixture_reset(0);self.d.open_cfw_bootloader_mspi_enable_41fe28();self.assertEqual(self.calls(),[1,2,1]);self.assertEqual(self.d.open_cfw_mspi_fixture_active(),1);self.d.open_cfw_bootloader_mspi_enable_41fe28();self.assertEqual(self.calls(),[1,2,1]);self.d.open_cfw_bootloader_mspi_disable_41fe48();self.assertEqual(self.calls(),[1,2,1,1,0,1]);self.assertEqual(self.d.open_cfw_mspi_fixture_active(),0)
 def test_target(self):
  o=Path(self.t.name)/'x.o';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(o)],check=True,capture_output=True)
if __name__=='__main__':unittest.main()
