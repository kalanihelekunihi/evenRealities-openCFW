from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/'components/bootloader/core_overlay/runtime_spotmgr_trim_commit_42ae9c.c';B=R/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';sys.path.insert(0,str(R/'tools'));import apollo_overlay  # noqa:E402
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/'c.dylib';subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-Wall','-Wextra','-Werror','-dynamiclib',str(S),'-o',str(p)],check=True,capture_output=True,text=True);c.f=ctypes.CDLL(str(p)).open_cfw_bootloader_spotmgr_trim_commit_42ae9c_portable;c.f.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32)]
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def test_gate(self):
  for pending,state,expected in ((0,0,0),(1,8,0),(1,12,0),(1,7,0x48)):
   v=ctypes.c_uint32(0);self.f(pending,state,ctypes.byref(v));self.assertEqual(v.value,expected)
 def test_exact(self):
  stock=B.read_bytes();
  for cc,v in ((Path('/usr/bin/clang'),'Apple clang version 21.0.0'),(Path('/opt/homebrew/opt/llvm@22/bin/clang'),'Homebrew clang version 22.1.8')):
   if not cc.exists():self.skipTest(str(cc))
   self.assertTrue(subprocess.run([str(cc),'--version'],check=True,capture_output=True,text=True).stdout.startswith(v));o=Path(self.t.name)/(cc.parent.name+'.o');subprocess.run([str(cc),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never','-c',str(S),'-o',str(o)],check=True,capture_output=True,text=True);d,s=apollo_overlay.parse_elf32(o);q=apollo_overlay.section_named(s,'.text.open_cfw_bootloader_spotmgr_trim_commit_42ae9c');body=bytearray(d[int(q['offset']):int(q['offset'])+int(q['size'])]);self.assertEqual(hashlib.sha256(body).hexdigest(),'0b2472da4b89f3dca0a6a8b877bcbb9f116587b6e8e9b4b18d609d218344a89e')
   for x,t in ((2,0x41b8ec),(8,0x42ae6c),(0x3e,0x41ccd6),(0x44,0x42ae24)):body[x:x+4]=apollo_overlay.encode_thumb_bl(0x42ae9c+x,t)
   self.assertEqual(bytes(body),stock[0x1ae9c:0x1aeec])
if __name__=='__main__':unittest.main()
