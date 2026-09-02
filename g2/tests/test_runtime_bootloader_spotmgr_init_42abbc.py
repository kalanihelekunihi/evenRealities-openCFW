from __future__ import annotations
import ctypes, hashlib, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'components/bootloader/core_overlay/runtime_spotmgr_init_42abbc.c'
BOOT=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'; BASE=0x410000
sys.path.insert(0,str(ROOT/'tools')); import apollo_overlay  # noqa: E402
READ=ctypes.CFUNCTYPE(ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_void_p)
INIT=ctypes.CFUNCTYPE(None,ctypes.c_void_p)
class State(ctypes.Structure): _fields_=[('words',ctypes.c_uint32*27)]

class SpotmgrInitTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory(); cls.libpath=Path(cls.t.name)/'init.dylib'
  subprocess.run([os.environ.get('CC','/usr/bin/clang'),'-std=c11','-Wall','-Wextra','-Werror','-dynamiclib',str(SOURCE),'-o',str(cls.libpath)],check=True,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(cls.libpath)); cls.fn=cls.lib.open_cfw_bootloader_spotmgr_init_42abbc
  cls.fn.argtypes=[ctypes.POINTER(State),ctypes.c_uint32,ctypes.c_uint32,READ,INIT,ctypes.c_void_p];cls.fn.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls): cls.t.cleanup()
 def test_read_sequence_commit_and_gating(self):
  calls=[]
  @READ
  def read(block,offset,words,dst,_):
   calls.append((block,offset,words));
   for i in range(words): dst[i]=offset+i
   return 0
  @INIT
  def init(_): calls.append(('init',))
  state=State();self.assertEqual(self.fn(ctypes.byref(state),0,0,read,init,None),0)
  self.assertEqual(calls,[(1,0x25c,20),(1,0x270,5),(1,0x278,1),('init',)])
  self.assertEqual(state.words[0],0x1f01600d);self.assertEqual(state.words[21],0x270);self.assertEqual(state.words[26],0x278)
  calls.clear();self.assertEqual(self.fn(ctypes.byref(state),8,0,read,init,None),7);self.assertEqual(calls,[])
 def test_error_short_circuits_each_read(self):
  for fail in range(3):
   calls=[]
   @READ
   def read(_b,_o,_w,_d,_c):
    calls.append(1);return 9 if len(calls)-1==fail else 0
   @INIT
   def init(_): self.fail('init must not run')
   self.assertEqual(self.fn(ctypes.byref(State()),0,0,read,init,None),9)
   self.assertEqual(len(calls),fail+1)
 def test_dispatch_pointer_and_exact_dual_toolchain_body(self):
  boot=BOOT.read_bytes();self.assertEqual(int.from_bytes(boot[0xd14c:0xd150],'little'),0x42abbd)
  for clang,version in ((Path('/usr/bin/clang'),'Apple clang version 21.0.0'),(Path('/opt/homebrew/opt/llvm@22/bin/clang'),'Homebrew clang version 22.1.8')):
   if not clang.exists():self.skipTest(str(clang))
   self.assertTrue(subprocess.run([str(clang),'--version'],check=True,capture_output=True,text=True).stdout.startswith(version))
   out=Path(self.t.name)/(clang.parent.name+'.o');subprocess.run([str(clang),'-target','arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror','-fno-ident','-mllvm','-enable-machine-outliner=never','-c',str(SOURCE),'-o',str(out)],check=True,capture_output=True,text=True)
   data,secs=apollo_overlay.parse_elf32(out);sec=apollo_overlay.section_named(secs,'.text.open_cfw_bootloader_spotmgr_init_42abbc');body=bytearray(data[int(sec['offset']):int(sec['offset'])+int(sec['size'])])
   self.assertEqual(hashlib.sha256(body).hexdigest(),'d62bfd5f7ca5b79c01d63f55da969f21f422c5503ded4857cf20312f5cfc4a7a')
   for off,target in ((0x3a,0x421548),(0x4c,0x421548),(0x72,0x421548),(0x88,0x41cc04)):body[off:off+4]=apollo_overlay.encode_thumb_bl(0x42abbc+off,target)
   self.assertEqual(bytes(body),boot[0x1abbc:0x1ac4e])
if __name__=='__main__':unittest.main()
