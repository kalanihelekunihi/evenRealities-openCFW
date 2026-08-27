from __future__ import annotations
import ctypes,hashlib,os,random,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_bit_helpers_host.c';SOURCES=tuple(ROOT/'components/bootloader/core_overlay'/name for name in ('runtime_bit_width_4169a4.c','runtime_ctz_4169e2.c','runtime_log2_4169f2.c'))
class BootloaderRuntimeBitHelpersTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory();p=Path(cls.t.name)/('bits.'+('dylib' if sys.platform=='darwin' else 'so'));cmd=[os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE)]+(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC'])+['-o',str(p)];subprocess.run(cmd,check=True,capture_output=True,text=True);cls.lib=ctypes.CDLL(str(p))
  for n in ('bit_width_4169a4','ctz_4169e2','log2_4169f2'):f=getattr(cls.lib,'open_cfw_bootloader_runtime_'+n);f.argtypes=[ctypes.c_uint32];f.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def test_authenticated_complete_bodies_and_callers(self):
  b=OFFICIAL.read_bytes();cases=((0x69A4,0x69E2,'a3a7efceaf507b98b5ba00ead31f0713ef289324a180c1d017b50db781d57d0f',(0x69EA,0x69F4),('fff7dbff','fff7d6ff')),(0x69E2,0x69F2,'32c3e2591f32bbda0aae71b2b2f742e3dd76405163ed9f53a40086a51d8119ef',(0x6C86,0x6CB0),('fff7acfe','fff797fe')),(0x69F2,0x69FC,'da2cf0f5cd806a2ec1fddd96dbf2770c4421098b26bc3380c539d5b83428d126',(0x6C10,0x6C36),('fff7effe','fff7dcfe')))
  for s,e,d,callers,callbytes in cases:self.assertEqual((e-s,hashlib.sha256(b[s:e]).hexdigest()),(e-s,d));self.assertEqual(tuple(b[o:o+4].hex() for o in callers),callbytes)
 def test_exact_width_ctz_log2_contracts(self):
  width=self.lib.open_cfw_bootloader_runtime_bit_width_4169a4;ctz=self.lib.open_cfw_bootloader_runtime_ctz_4169e2;log2=self.lib.open_cfw_bootloader_runtime_log2_4169f2
  values=[0,1,2,3,4,7,8,0x7fffffff,0x80000000,0xffffffff]+[random.Random(0x4169A4).getrandbits(32) for _ in range(256)]
  for v in values:
   self.assertEqual(width(v),v.bit_length());self.assertEqual(log2(v),((v.bit_length()-1)&0xffffffff));self.assertEqual(ctz(v),(((((v&-v)&0xffffffff).bit_length()-1))&0xffffffff))
 def test_freestanding_targets_compile(self):
  flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c']
  for s in SOURCES:subprocess.run(flags+[str(s),'-o',str(Path(self.t.name)/(s.stem+'.o'))],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
