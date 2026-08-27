from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_queue_create_416816_host.c';SOURCE=ROOT/'components/bootloader/core_overlay/runtime_queue_create_416816.c'
class BootloaderRuntimeQueueCreate416816Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory();p=Path(cls.t.name)/('q.'+('dylib' if sys.platform=='darwin' else 'so'));cmd=[os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE)]+(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC'])+['-o',str(p)];subprocess.run(cmd,check=True,capture_output=True,text=True);cls.lib=ctypes.CDLL(str(p));w=ctypes.c_size_t
  class Config(ctypes.Structure):_fields_=[('name',w),('attributes',w),('control_storage',w),('control_storage_size',w),('message_storage',w),('message_storage_size',w)]
  cls.Config=Config;cls.lib.open_cfw_test_queue_reset.argtypes=[w,w];cls.lib.open_cfw_bootloader_runtime_queue_create_416816.argtypes=[w,w,ctypes.POINTER(Config)];cls.lib.open_cfw_bootloader_runtime_queue_create_416816.restype=w
  for n in ('static_calls','dynamic_calls','observed_count','observed_size','observed_messages','observed_control','observed_kind'):getattr(cls.lib,'open_cfw_test_queue_'+n).restype=w
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def test_authenticated_body_and_callers(self):
  b=OFFICIAL.read_bytes();raw=b[0x6816:0x68A2];self.assertEqual((len(raw),hashlib.sha256(raw).hexdigest()),(140,'0529769ef0cd634c8a643a7c412f804d9c530fcc2e5b54a87b532b8ec3fb583a'));self.assertEqual([b[o:o+4].hex() for o in (0x1DD7C,0x1E550)],['e8f74bfd','e8f761f9'])
 def test_guards_and_invalid_mixed_storage(self):
  cases=[(1,2,3,None),(0,0,3,None),(0,2,0,None),(0,2,3,self.Config(0,0,1,79,2,6)),(0,2,3,self.Config(0,0,0,0,1,6))]
  for critical,count,size,cfg in cases:
   self.lib.open_cfw_test_queue_reset(critical,9);p=None if cfg is None else ctypes.byref(cfg);self.assertEqual(self.lib.open_cfw_bootloader_runtime_queue_create_416816(count,size,p),0);self.assertEqual(self.lib.open_cfw_test_queue_static_calls()+self.lib.open_cfw_test_queue_dynamic_calls(),0)
 def test_dynamic_null_and_empty_config(self):
  for cfg in (None,self.Config(0,0,0,0,0,0)):
   self.lib.open_cfw_test_queue_reset(0,0x200);p=None if cfg is None else ctypes.byref(cfg);self.assertEqual(self.lib.open_cfw_bootloader_runtime_queue_create_416816(4,8,p),0x200);self.assertEqual(self.lib.open_cfw_test_queue_dynamic_calls(),1);self.assertEqual(self.lib.open_cfw_test_queue_observed_kind(),0)
 def test_static_storage_threshold_and_argument_order(self):
  control=(ctypes.c_uint8*80)();messages=(ctypes.c_uint8*32)();cfg=self.Config(0,0,ctypes.addressof(control),80,ctypes.addressof(messages),32);self.lib.open_cfw_test_queue_reset(0,0x300);self.assertEqual(self.lib.open_cfw_bootloader_runtime_queue_create_416816(4,8,ctypes.byref(cfg)),0x300);self.assertEqual(self.lib.open_cfw_test_queue_static_calls(),1);self.assertEqual((self.lib.open_cfw_test_queue_observed_count(),self.lib.open_cfw_test_queue_observed_size(),self.lib.open_cfw_test_queue_observed_messages(),self.lib.open_cfw_test_queue_observed_control(),self.lib.open_cfw_test_queue_observed_kind()),(4,8,ctypes.addressof(messages),ctypes.addressof(control),0))
 def test_freestanding_target_compiles(self):subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(Path(self.t.name)/'q.o')],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
