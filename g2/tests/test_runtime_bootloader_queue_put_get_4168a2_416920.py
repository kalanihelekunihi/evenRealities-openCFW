from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
FIXTURE=ROOT/'tests/fixtures/bootloader_runtime_queue_put_get_host.c'
SOURCES=(ROOT/'components/bootloader/core_overlay/runtime_queue_put_4168a2.c',ROOT/'components/bootloader/core_overlay/runtime_queue_get_416920.c')
class BootloaderRuntimeQueuePutGetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory();p=Path(cls.t.name)/('qio.'+('dylib' if sys.platform=='darwin' else 'so'));cmd=[os.environ.get('CC','/usr/bin/clang'),'-std=c11','-O2','-Wall','-Wextra','-Werror',str(FIXTURE)]+(['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC'])+['-o',str(p)];subprocess.run(cmd,check=True,capture_output=True,text=True);cls.lib=ctypes.CDLL(str(p));w=ctypes.c_size_t
  cls.lib.open_cfw_test_queue_io_reset.argtypes=[ctypes.c_uint32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32,ctypes.c_int32];cls.lib.open_cfw_test_queue_put.argtypes=[w,w,ctypes.c_uint8,ctypes.c_uint32];cls.lib.open_cfw_test_queue_put.restype=ctypes.c_int32;cls.lib.open_cfw_test_queue_get.argtypes=[w,w,w,ctypes.c_uint32];cls.lib.open_cfw_test_queue_get.restype=ctypes.c_int32;cls.lib.open_cfw_test_queue_io_observed.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_test_queue_io_observed.restype=w
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def reset(self,critical=0,put_isr=1,put_task=1,get_isr=1,get_task=1,yield_value=0):self.lib.open_cfw_test_queue_io_reset(critical,put_isr,put_task,get_isr,get_task,yield_value)
 def obs(self,n):return self.lib.open_cfw_test_queue_io_observed(n)
 def test_authenticated_complete_bodies_callers_and_literal_pool(self):
  b=OFFICIAL.read_bytes();cases=((0x68A2,0x6920,'91e5690abdb827a51e097c4a062fe375df5157e3f2039d736b298b22e04868be',(0x1DCDA,0x1E6C8),('e8f7e2fd','e8f7ebf8')),(0x6920,0x699A,'314c0a49b1cd6147c22638e354ac5e1fc82bf310547a5fb38a897f4f263c784e',(0x1DEA8,0x1E65E),('e8f73afd','e8f75ff9')))
  for start,end,digest,callers,callbytes in cases:self.assertEqual((end-start,hashlib.sha256(b[start:end]).hexdigest()),(end-start,digest));self.assertEqual(tuple(b[o:o+4].hex() for o in callers),callbytes)
  self.assertEqual((b[0x699A:0x69A4].hex(),hashlib.sha256(b[0x699A:0x69A4]).hexdigest()),('000004ed00e09b634100','cee9e0dc13ea1c82bfb1368348df84ffab973c1fe17cce15036de271d685d310'))
 def test_isr_guards_results_and_pendsv(self):
  for call in (self.lib.open_cfw_test_queue_put,self.lib.open_cfw_test_queue_get):
   for q,m,t in ((0,2,0),(1,0,0),(1,2,1)):
    self.reset(critical=1);self.assertEqual(call(q,m,255,t),-4);self.assertEqual(sum(self.obs(i) for i in range(4)),0)
  self.reset(critical=1,put_isr=0,yield_value=1);self.assertEqual(self.lib.open_cfw_test_queue_put(1,2,255,0),-3);self.assertEqual(self.obs(4),0)
  self.reset(critical=1,get_isr=0,yield_value=1);self.assertEqual(self.lib.open_cfw_test_queue_get(1,2,0x3333,0),-3);self.assertEqual(self.obs(4),0)
  self.reset(critical=1,yield_value=1);self.assertEqual(self.lib.open_cfw_test_queue_put(1,2,255,0),0);self.assertEqual(self.obs(4),1)
  self.reset(critical=1,yield_value=1);self.assertEqual(self.lib.open_cfw_test_queue_get(1,2,0x3333,0),0);self.assertEqual(self.obs(4),1)
 def test_task_status_mapping_and_arguments(self):
  for call,task_selector in ((self.lib.open_cfw_test_queue_put,1),(self.lib.open_cfw_test_queue_get,3)):
   self.reset();self.assertEqual(call(0,2,255,0),-4);self.assertEqual(call(1,0,255,0),-4)
   if task_selector==1:self.reset(put_task=0)
   else:self.reset(get_task=0)
   self.assertEqual(call(0x1111,0x2222,255,0),-3)
   if task_selector==1:self.reset(put_task=0)
   else:self.reset(get_task=0)
   self.assertEqual(call(0x1111,0x2222,255,9),-2)
   self.reset();self.assertEqual(call(0x1111,0x2222,255,9),0);self.assertEqual((self.obs(task_selector),self.obs(5),self.obs(6),self.obs(7)),(1,0x1111,0x2222,9))
  self.reset();self.assertEqual(self.lib.open_cfw_test_queue_put(1,2,255,7),0);self.assertEqual(self.obs(8),0)
 def test_freestanding_targets_compile(self):
  flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c']
  for source in SOURCES:subprocess.run(flags+[str(source),'-o',str(Path(self.t.name)/(source.stem+'.o'))],check=True,capture_output=True,text=True)
if __name__=='__main__':unittest.main()
