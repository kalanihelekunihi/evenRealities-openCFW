from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/'components/bootloader/core_overlay/runtime_spotmgr_trim_helpers_42adb8.c';B=R/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';sys.path.insert(0,str(R/'tools'));import apollo_overlay  # noqa:E402
SPECS=(('open_cfw_bootloader_spotmgr_trim_enable_42adb8',0x42adb8,0x42ae24,'7b25d7dae842d5787345a5360a32fbf21f4adadc88e216b2eaa272cc77d7feda'),('open_cfw_bootloader_spotmgr_profile_trim_42ae24',0x42ae24,0x42ae6c,'73da1f0b69f23d583009d5dfbc2f46007ee0f8b9f56a5c8a3b4fccd58136f538'),('open_cfw_bootloader_spotmgr_trim_restore_42ae6c',0x42ae6c,0x42ae9c,'fbc7ca52270345ca6b251d1c8c805a06e33af456500f9b17e05cfa7743af79f8'))
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/'h.dylib';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-Wall','-Wextra','-Werror','-dynamiclib',str(S),'-o',str(p)],check=True,capture_output=True,text=True);c.l=ctypes.CDLL(str(p))
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def test_portable_bitfield_semantics(self):
  u=ctypes.c_uint32;f=self.l.open_cfw_bootloader_spotmgr_trim_enable_42adb8;f.argtypes=[u,u,u]+[ctypes.POINTER(u)]*4;c,p,t,h=u(0),u(0xffff0000),u(0xabc003fc),u();f(1,0x12345678,9,ctypes.byref(c),ctypes.byref(p),ctypes.byref(t),ctypes.byref(h));self.assertEqual(c.value,0x18000);self.assertEqual(p.value&0x3f,(0x12345678>>14)&0x3f);self.assertEqual(h.value,3);self.assertEqual(t.value&0x3ff,5)
  g=self.l.open_cfw_bootloader_spotmgr_profile_trim_42ae24;g.argtypes=[u,u,u]+[ctypes.POINTER(u)]*3;a,b,q=u(0),u(0),u(3);g(1,0x7b,5,ctypes.byref(a),ctypes.byref(b),ctypes.byref(q));self.assertEqual(a.value&0x3f,(0x7b>>2)&0x3f);self.assertEqual((b.value>>15)&3,3);self.assertEqual(q.value&0x3ff,0x3fe)
  k=self.l.open_cfw_bootloader_spotmgr_trim_restore_42ae6c;k.argtypes=[u,u,u,ctypes.POINTER(u),ctypes.POINTER(u)];x,y=u(0xffffff80),u(0xffffff80);k(0,5,7,ctypes.byref(x),ctypes.byref(y));self.assertEqual(x.value&0x7f,5);self.assertEqual(y.value&0x7f,7)
 def test_exact_dual(self):
  stock=B.read_bytes()
  for cc,v in ((Path('/usr/bin/clang'),'Apple clang version 21.0.0'),(Path('/opt/homebrew/opt/llvm@22/bin/clang'),'Homebrew clang version 22.1.8')):
   if not cc.exists():self.skipTest(str(cc))
   self.assertTrue(subprocess.run([str(cc),'--version'],check=True,capture_output=True,text=True).stdout.startswith(v));o=Path(self.t.name)/(cc.parent.name+'.o');subprocess.run([str(cc),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never','-c',str(S),'-o',str(o)],check=True,capture_output=True,text=True);d,s=apollo_overlay.parse_elf32(o)
   for f,a,z,h in SPECS:q=apollo_overlay.section_named(s,'.text.'+f);body=d[int(q['offset']):int(q['offset'])+int(q['size'])];self.assertEqual(body,stock[a-0x410000:z-0x410000]);self.assertEqual(hashlib.sha256(body).hexdigest(),h)
if __name__=='__main__':unittest.main()
