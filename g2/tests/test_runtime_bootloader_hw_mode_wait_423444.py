from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_mode_wait_423444.c"
FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_hw_mode_wait_host.c"
class Instance(ctypes.Structure): _fields_=[("bytes",ctypes.c_uint8*0x11c)]
class Request(ctypes.Structure): _fields_=[("bytes",ctypes.c_uint8*0x38)]

class BootloaderHardwareModeWaitTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(); out=Path(cls.tmp.name)/("hwmw.dylib" if sys.platform=="darwin" else "hwmw.so")
  subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(out)],check=True,capture_output=True)
  cls.lib=ctypes.CDLL(str(out)); cls.zero=cls.lib.open_cfw_bootloader_hw_mode_zero_wait_423444; cls.one=cls.lib.open_cfw_bootloader_hw_mode_one_wait_42348e
  for f in (cls.zero,cls.one): f.argtypes=[ctypes.POINTER(Instance),ctypes.POINTER(Request)]; f.restype=ctypes.c_uint32
  for n in ("mode_two_result","mode_three_result","mode_two_count","mode_three_count","primary_progress_count","secondary_progress_count","primary_clear_after","secondary_clear_after","delay_count","delay_value"): setattr(cls,n,ctypes.c_uint32.in_dll(cls.lib,"open_cfw_hwmw_host_"+n))
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def setUp(self):
  for n in ("mode_two_result","mode_three_result","mode_two_count","mode_three_count","primary_progress_count","secondary_progress_count","primary_clear_after","secondary_clear_after","delay_count","delay_value"): getattr(self,n).value=0
  self.i=Instance(); self.r=Request()
 def timeout(self,value):
  for k in range(4): self.r.bytes[0xc+k]=(value>>(8*k))&255
 def test_authenticated_bodies_and_boundaries(self):
  b=OFFICIAL.read_bytes(); self.assertEqual(hashlib.sha256(b[0x13444:0x1348e]).hexdigest(),"274da3564e8944b5355109d064af8bc74a1c69be2fa349865db47fe99ec4326e"); self.assertEqual(hashlib.sha256(b[0x1348e:0x134d8]).hexdigest(),"dbeaa29a43e7f7c9e92a611782d56c41adea8d11fca90f6921f4b70bbcb5cd72")
 def test_start_errors_return_without_polling(self):
  self.mode_two_result.value=7; self.mode_three_result.value=8
  self.assertEqual(self.zero(ctypes.byref(self.i),ctypes.byref(self.r)),7); self.assertEqual(self.one(ctypes.byref(self.i),ctypes.byref(self.r)),8); self.assertEqual(self.delay_count.value,0)
 def test_primary_wait_completes_when_progress_clears_active(self):
  self.i.bytes[0x119]=1; self.primary_clear_after.value=2; self.timeout(5)
  self.assertEqual(self.zero(ctypes.byref(self.i),ctypes.byref(self.r)),0); self.assertEqual((self.primary_progress_count.value,self.delay_count.value,self.delay_value.value),(2,2,1000))
 def test_secondary_wait_times_out_and_clears_active(self):
  self.i.bytes[0x11a]=1; self.timeout(3)
  self.assertEqual(self.one(ctypes.byref(self.i),ctypes.byref(self.r)),4); self.assertEqual((self.secondary_progress_count.value,self.i.bytes[0x11a]),(3,0))
 def test_source_cross_compiles(self):
  for c in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(c).exists(): subprocess.run([c,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(self.tmp.name)/(Path(c).parent.name+"-hwmw.o"))],check=True,capture_output=True)
if __name__=="__main__": unittest.main()
