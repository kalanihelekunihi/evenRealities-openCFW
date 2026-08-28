from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';SOURCE=ROOT/'components/bootloader/core_overlay/runtime_irq_services_41fdc0.c';FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_irq_services_host.c';BASE=0x410000
SPANS=((0x41FDC0,0x41FDDE,'6fbb6367b6801ee7979acd72367d57b54bd1c55c41b17f7a70365bcd94b8991c'),(0x41FDDE,0x41FE06,'1fa388746ea65ab90eb2ad94d86503527e74b1bd1a24a3b2b5c6491059d93011'),(0x41FE06,0x41FE28,'35d4b9a6550f30c232ef637ab736df92e1ffca38fc55af1ccdc0da43bffd3236'))
def bl(b,a):
 o=a-BASE;f=int.from_bytes(b[o:o+2],'little');s=int.from_bytes(b[o+2:o+4],'little')
 if f&0xf800!=0xf000 or s&0xd000!=0xd000:return None
 sign=f>>10&1;i1=1^(s>>13&1)^sign;i2=1^(s>>11&1)^sign;v=(sign<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if v&1<<24:v-=1<<25
 return a+4+v
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();c.l=Path(c.t.name)/('x.dylib' if sys.platform=='darwin' else 'x.so');subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE),*(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC']),'-o',str(c.l)],check=True,capture_output=True,text=True);c.d=ctypes.CDLL(str(c.l));c.d.open_cfw_irq_fixture_call.restype=ctypes.c_uint32;c.d.open_cfw_irq_fixture_count.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def calls(self):return [self.d.open_cfw_irq_fixture_call(i) for i in range(self.d.open_cfw_irq_fixture_count())]
 def test_stock_ingress(self):
  b=OFFICIAL.read_bytes()
  for a,z,h in SPANS:self.assertEqual(hashlib.sha256(b[a-BASE:z-BASE]).hexdigest(),h)
  self.assertEqual(tuple(a for a in range(BASE,BASE+len(b)-3,2) if bl(b,a)==0x41FDC0),(0x420414,));self.assertEqual(tuple(a for a in range(BASE,BASE+len(b)-3,2) if bl(b,a)==0x41FDDE),(0x42040E,));self.assertEqual(int.from_bytes(b[0x94:0x98],'little'),0x41FE07)
 def test_nvic_semantics(self):
  self.d.open_cfw_irq_fixture_reset(0);self.d.open_cfw_bootloader_nvic_enable_irq_41fdc0(35);self.assertEqual(self.calls(),[0x10000001,8]);self.d.open_cfw_irq_fixture_reset(0);self.d.open_cfw_bootloader_nvic_enable_irq_41fdc0(0xFFFF);self.assertEqual(self.calls(),[])
  self.d.open_cfw_irq_fixture_reset(0);self.d.open_cfw_bootloader_nvic_set_priority_41fdde(7,0x13);self.assertEqual(self.calls(),[0x20000007,0x30]);self.d.open_cfw_irq_fixture_reset(0);self.d.open_cfw_bootloader_nvic_set_priority_41fdde(0xFFFFFFFF,6);self.assertEqual(self.calls(),[0x3000000B,0x60])
 def test_mspi_order(self):
  self.d.open_cfw_irq_fixture_reset(0xA5A55A5A);self.d.open_cfw_bootloader_mspi_isr_41fe06();self.assertEqual(self.calls(),[0x40000000,0x50000000,0,0x60000000,0xA5A55A5A,0x70000000,0xA5A55A5A])
 def test_target(self):
  o=Path(self.t.name)/'x.o';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(o)],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
