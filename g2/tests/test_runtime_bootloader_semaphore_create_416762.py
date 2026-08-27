from __future__ import annotations
import ctypes, hashlib, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'; FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_semaphore_create_416762_host.c'; SOURCE=ROOT/'components/bootloader/core_overlay/runtime_semaphore_create_416762.c'
class BootloaderRuntimeSemaphoreCreate416762Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory(); suffix='dylib' if sys.platform=='darwin' else 'so'; cls.p=Path(cls.t.name)/('sem.'+suffix); cmd=[os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE)]+(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC'])+['-o',str(cls.p)];subprocess.run(cmd,check=True,capture_output=True,text=True);cls.lib=ctypes.CDLL(str(cls.p));w=ctypes.c_size_t
  class Config(ctypes.Structure):_fields_=[('name',w),('attributes',w),('storage',w),('storage_size',w)]
  cls.Config=Config;cls.lib.open_cfw_test_semaphore_reset.argtypes=[w,w,w];cls.lib.open_cfw_bootloader_runtime_semaphore_create_416762.argtypes=[w,w,ctypes.POINTER(Config)];cls.lib.open_cfw_bootloader_runtime_semaphore_create_416762.restype=w
  for n in ('binary_static_calls','binary_dynamic_calls','count_static_calls','count_dynamic_calls','release_calls','delete_calls','observed_maximum','observed_initial','observed_storage','observed_kind','observed_zero_arguments'):getattr(cls.lib,'open_cfw_test_semaphore_'+n).restype=w
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def calls(self):return sum(getattr(self.lib,'open_cfw_test_semaphore_'+n)() for n in ('binary_static_calls','binary_dynamic_calls','count_static_calls','count_dynamic_calls'))
 def test_authenticated_stock_body_and_caller(self):
  b=OFFICIAL.read_bytes();raw=b[0x6762:0x6816];self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(180,'48c3940e6f762adfbdbef5d40813bfcc043edd10947ad93982c1b8c1051a410f'));self.assertEqual(b[0x205E0:0x205E4].hex(),'e6f7bff8')
 def test_guards_and_storage_contract(self):
  cases=[(1,1,0,None),(0,0,0,None),(0,1,2,None),(0,2,0,self.Config(0,0,1,79)),(0,2,0,self.Config(0,0,0,1))]
  for critical,maximum,initial,config in cases:
   self.lib.open_cfw_test_semaphore_reset(critical,0x200,1);p=None if config is None else ctypes.byref(config);self.assertEqual(self.lib.open_cfw_bootloader_runtime_semaphore_create_416762(maximum,initial,p),0);self.assertEqual(self.calls(),0)
 def test_binary_dynamic_and_initial_give(self):
  for initial,gives in ((0,0),(1,1)):
   self.lib.open_cfw_test_semaphore_reset(0,0x200,1);self.assertEqual(self.lib.open_cfw_bootloader_runtime_semaphore_create_416762(1,initial,None),0x200);self.assertEqual(self.lib.open_cfw_test_semaphore_binary_dynamic_calls(),1);self.assertEqual(self.lib.open_cfw_test_semaphore_observed_kind(),3);self.assertEqual(self.lib.open_cfw_test_semaphore_release_calls(),gives);self.assertEqual(self.lib.open_cfw_test_semaphore_observed_zero_arguments(),0)
 def test_binary_static_and_failed_give_cleanup(self):
  storage=(ctypes.c_uint8*80)();cfg=self.Config(0,0,ctypes.addressof(storage),80);self.lib.open_cfw_test_semaphore_reset(0,0x220,0);self.assertEqual(self.lib.open_cfw_bootloader_runtime_semaphore_create_416762(1,1,ctypes.byref(cfg)),0);self.assertEqual(self.lib.open_cfw_test_semaphore_binary_static_calls(),1);self.assertEqual(self.lib.open_cfw_test_semaphore_release_calls(),1);self.assertEqual(self.lib.open_cfw_test_semaphore_delete_calls(),1);self.assertEqual(self.lib.open_cfw_test_semaphore_observed_storage(),0x220)
 def test_counting_static_and_dynamic(self):
  storage=(ctypes.c_uint8*80)();cfg=self.Config(0,0,ctypes.addressof(storage),80)
  for pointer,static in ((None,False),(ctypes.byref(cfg),True)):
   self.lib.open_cfw_test_semaphore_reset(0,0x330,1);self.assertEqual(self.lib.open_cfw_bootloader_runtime_semaphore_create_416762(5,3,pointer),0x330);self.assertEqual(self.lib.open_cfw_test_semaphore_count_static_calls(),int(static));self.assertEqual(self.lib.open_cfw_test_semaphore_count_dynamic_calls(),int(not static));self.assertEqual(self.lib.open_cfw_test_semaphore_observed_maximum(),5);self.assertEqual(self.lib.open_cfw_test_semaphore_observed_initial(),3)
 def test_freestanding_target_compiles(self):
  subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(Path(self.t.name)/'sem.o')],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
