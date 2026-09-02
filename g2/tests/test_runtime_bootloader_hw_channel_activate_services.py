import ctypes, hashlib, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=[ROOT/"components/bootloader/core_overlay/runtime_hw_channel_config_42eaf6.c",
         ROOT/"components/bootloader/core_overlay/runtime_hw_handle_activate_42ed60.c"]
BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never")
PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
ITEMS=(("open_cfw_bootloader_hw_channel_config_42eaf6",0x42EAF6,126,"59424a9cdea76c34a98142a28944d1d1700758cc2412e7d1903be4757e1d3c04",0x55DB72,SOURCES[0]),
       ("open_cfw_bootloader_hw_handle_activate_42ed60",0x42ED60,64,"5603c205e322271c30b9c91be82538938549b50a35f8e6d1ad94de5d1bb7eb23",0x55DDDC,SOURCES[1]))
class Handle(ctypes.Structure):_fields_=[("word0",ctypes.c_uint32),("word1",ctypes.c_uint32)]
class Config(ctypes.Structure):_fields_=[("byte0",ctypes.c_uint8),("pad1",ctypes.c_uint8),("pad2",ctypes.c_uint8),("pad3",ctypes.c_uint8),("word4",ctypes.c_uint32),("byte8",ctypes.c_uint8),("byte9",ctypes.c_uint8),("byte10",ctypes.c_uint8),("byte11",ctypes.c_uint8)]
class Regs(ctypes.Structure):_fields_=[("channel",ctypes.c_uint32*8),("update_count",ctypes.c_uint32)]
class TestServices(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"x.so";cc=shutil.which("cc") or shutil.which("clang")
  subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",*[str(x) for x in SOURCES],"-o",str(lib)],check=True);dll=ctypes.CDLL(str(lib))
  cls.channel=dll.open_cfw_bootloader_hw_channel_config_42eaf6_portable;cls.channel.argtypes=[ctypes.POINTER(Handle),ctypes.c_uint32,ctypes.POINTER(Config),ctypes.POINTER(Regs)];cls.channel.restype=ctypes.c_uint32
  cls.activate=dll.open_cfw_bootloader_hw_handle_activate_42ed60_portable;cls.activate.argtypes=[ctypes.POINTER(Handle),ctypes.POINTER(ctypes.c_uint32)];cls.activate.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_semantics(self):
  h=Handle(0x01AFAFAF,0);r=Regs();c=Config(7,0,0,0,63,3,15,0xAA,1)
  self.assertEqual(self.channel(ctypes.byref(h),7,ctypes.byref(c),ctypes.byref(r)),0)
  expected=(7<<24)|(63<<18)|(3<<16)|(15<<8)|(0xAA<<1)|1
  self.assertEqual((r.channel[7],r.update_count),(expected,1))
  self.assertEqual(self.channel(ctypes.byref(h),8,ctypes.byref(c),ctypes.byref(r)),5);c.word4=31;self.assertEqual(self.channel(ctypes.byref(h),0,ctypes.byref(c),ctypes.byref(r)),6)
  control=ctypes.c_uint32(0x10);self.assertEqual(self.activate(ctypes.byref(h),ctypes.byref(control)),0);self.assertEqual(control.value,0x11);before=control.value;self.assertEqual(self.activate(ctypes.byref(h),ctypes.byref(control)),0);self.assertEqual(control.value,before)
 def test_exact(self):
  b=BOOT.read_bytes();m=MAIN.read_bytes()
  with tempfile.TemporaryDirectory() as d:
   for cc in PROFILES:
    for function,start,size,digest,main_start,source in ITEMS:
     obj=Path(d)/(function+cc.name+".o");subprocess.run([str(cc),*FLAGS,"-c",str(source),"-o",str(obj)],check=True)
     stock=b[start-0x410000:start-0x410000+size];analogue=m[main_start-0x437fe0:main_start-0x437fe0+size]
     self.assertEqual(hashlib.sha256(stock).hexdigest(),digest);self.assertEqual(stock,analogue)
     linked,report=apollo_overlay.extract_in_place_function_section(obj,function,runtime_address=start,relocation_configs=[],strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(linked,stock);self.assertEqual(report["relocation_count"],0)
 def test_reviewable(self):
  for source in SOURCES:
   text=source.read_text();self.assertIn("SPDX-License-Identifier: MIT",text)
   for token in (".byte",".short",".word",".inst"):self.assertNotIn(token,text)
if __name__=="__main__":unittest.main()
