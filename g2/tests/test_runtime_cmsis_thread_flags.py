from __future__ import annotations
import ctypes,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/shared/freertos/runtime_freertos_task_notify.c';HEADER=SOURCE.with_suffix('.h');CMSIS=ROOT/'components/apollo_main/core_overlay/runtime_cmsis_thread_flags.c';FIXTURE=ROOT/'tests/fixtures/runtime_cmsis_thread_flags_host.c';OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
class RuntimeCmsisThreadFlagsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();clang=os.environ.get('OPENCFW_CLANG','/usr/bin/clang');lib=Path(cls.tmp.name)/('f.dylib' if sys.platform=='darwin' else 'f.so');cmd=[clang,'-O2','-Wall','-Wextra','-Werror',str(FIXTURE),'-dynamiclib' if sys.platform=='darwin' else '-shared'];
  if sys.platform!='darwin':cmd.append('-fPIC')
  subprocess.run([*cmd,'-o',str(lib)],check=True,capture_output=True);cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_thread_flags_host_reset.argtypes=[ctypes.c_uint32]*2
  for n in ('set_target','set_current','set_yield_notification'):getattr(cls.lib,'open_cfw_thread_flags_host_'+n).argtypes=[ctypes.c_uint32]*({'set_target':3,'set_current':2,'set_yield_notification':2}[n])
  for n in ('set_irq','set_suspended','set_tick'):getattr(cls.lib,'open_cfw_thread_flags_host_'+n).argtypes=[ctypes.c_uint32]
  cls.lib.open_cfw_thread_flags_host_notify.argtypes=[ctypes.c_uint32]*4+[ctypes.POINTER(ctypes.c_uint32)]*2;cls.lib.open_cfw_thread_flags_host_notify.restype=ctypes.c_int32
  cls.lib.open_cfw_thread_flags_host_wait_kernel.argtypes=[ctypes.c_uint32]*3+[ctypes.POINTER(ctypes.c_uint32)];cls.lib.open_cfw_thread_flags_host_wait_kernel.restype=ctypes.c_int32
  cls.lib.open_cfw_thread_flags_host_set_wrapper.argtypes=[ctypes.c_uint32]*2;cls.lib.open_cfw_thread_flags_host_set_wrapper.restype=ctypes.c_uint32
  cls.lib.open_cfw_thread_flags_host_wait_wrapper.argtypes=[ctypes.c_uint32]*3;cls.lib.open_cfw_thread_flags_host_wait_wrapper.restype=ctypes.c_uint32
  cls.lib.open_cfw_thread_flags_host_get.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_thread_flags_host_get.restype=ctypes.c_size_t
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def reset(self,a=2,b=5):self.lib.open_cfw_thread_flags_host_reset(a,b)
 def get(self,n):return self.lib.open_cfw_thread_flags_host_get(n)
 def test_sources_and_exact_stock_boundaries_are_pinned(self):
  pins=[(SOURCE,8632,'e33a4a76b2f018fd191d10d1a9a3f1c1c777031e2a41c7b3a6b459d5cb07e2ab'),(HEADER,5578,'219414402dd88818dbf5ad0142346b8c8b8a65a136c10c72e2a97ab5c48b4534'),(CMSIS,3933,'59a3f67491f86c909334d6404d148461a5ecc2dbf15c374efefb8ddfa3a69ea1')]
  for p,s,h in pins:self.assertEqual((p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()),(s,h))
  b=OFFICIAL.read_bytes()[32:];base=0x438000
  spans=[(0x455b84,0x455c48,'3d55447f2a7a719bbc1752d7d1b07f19fee401f320ae4b61055cbec427515cc9'),(0x455c48,0x455db8,'fbcc2f27349099a2dc37ef103fc959730f14c6e0ef387507cbcba22fd3fc0a63'),(0x455dc0,0x455f5c,'53aaaae75cd8808438e70404f910072b52eb627d457b8eeda8961f1f4241c8e5'),(0x449238,0x4492c2,'c9e8658cde4a293b9d193cc15a854564445a8f399ad838450ef48c12eb9b6e11'),(0x4492c2,0x449376,'be6894be51ea1a3131610342eb0806c96d2ddc298e5642481d207263de96c4fe')]
  for a,z,h in spans:self.assertEqual(hashlib.sha256(b[a-base:z-base]).hexdigest(),h)
  self.assertEqual(hashlib.sha256(b[0x455c30-base:0x455c48-base]).hexdigest(),'1ec96cd94786c5816bd0b914c7711edba0a4e4100bd081d8ead515d32d0f6ba1')
 def test_dual_profile_production_admission_is_pinned(self):
  config=json.loads(OVERLAY.read_text());leaves={x['function']:x for x in config['relocated_leaves']}
  pins={'open_cfw_freertos_task_notify_wait':((130,136064,'9f84d2c30e86f3a01ef3639e7a54f7cc34d5901d41a0d1b093604a5da4b0117d'),(130,137944,'2a3781baa5f838bfbd5c8b8807056f87f7b8cb5f4452ca2a55cbbe93d2d41062')),'open_cfw_freertos_task_notify':((278,136196,'ddd1f57e472644ad41480839c6dad3826ce76aeca54aa261b911691c0b7ca6a5'),(278,138076,'8b39f0d6fa5d6c3a96f61c6e90095e4297b24d55087d61330dfd1f26e1689f89')),'open_cfw_freertos_task_notify_from_isr':((296,136476,'119baf4051e61f98958823be2b7c0dc844a20ba32f02e1c3fcef9de40fc9c20e'),(296,138356,'11bfdf1f0f0df5264de54589d0700f5494bedc71b8beb7451ec353be8787035c')),'open_cfw_cmsis_thread_flags_set':((130,136772,'b04f2432b294ea7c0fdb56bf95b63c1ec406e2d8c9ced165b7af450a7f2beaa9'),(132,138652,'570be208aa0d31a84ad7038a9715ac0a67170fa86f841671b41a921739c6f84c')),'open_cfw_cmsis_thread_flags_wait':((186,136904,'2f7b0ad828f7843694a2b0f407fe55d9bf1b9ef798c08238095cae1c0e9367d6'),(186,138784,'87946a64cfbe356e7e46e3cc063df7cbc7c57e75386fd89cbfe075f06a78c4a6'))}
  for name,(apple,linux) in pins.items():
   leaf=leaves[name];self.assertEqual((leaf['expected']['size'],leaf['expected']['offset'],leaf['expected']['sha256']),apple);p=leaf['toolchain_profiles']['linux-clang']['expected'];self.assertEqual((p['size'],p['offset'],p['sha256']),linux);self.assertTrue(leaf['strict_relocation_contract'])
  self.assertEqual((config['expected']['overlay_size'],config['expected']['overlay_sha256']),(142986,'1b0fc521cc8964da6525b7f7dce99060d07f5671f0038f37bcd998a56422a49f'));self.assertEqual((config['toolchain_profiles']['linux-clang']['expected']['overlay_size'],config['toolchain_profiles']['linux-clang']['expected']['overlay_sha256']),(144266,'4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9'))
  manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions={x['name']:x for x in main['regions']};self.assertEqual(tuple(regions[n]['file_offset'] for n in ('apollo_freertos_task_notify_wait_source_leaf','apollo_freertos_task_notify_source_leaf','apollo_freertos_task_notify_from_isr_source_leaf','apollo_cmsis_thread_flags_set_source_leaf','apollo_cmsis_thread_flags_wait_source_leaf')),(3659460,3659592,3659872,3660168,3660300));self.assertEqual((main['provider']['size'],main['provider']['sha256']),(3666382,'a4552ff210b6af33b7826a6b9aaefa6e01c7e6e976c9a852498570ededcf058f'));self.assertEqual((main['provider']['profiles']['linux-clang']['size'],main['provider']['profiles']['linux-clang']['sha256']),(3667662,'686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6'));self.assertEqual((manifest['package']['expected_size'],manifest['package']['expected_sha256']),(4444468,'53b240df100153c5453697fb3ce8ac66663ca82484a1d69f88345e1e7c3cd3c6'));self.assertEqual((manifest['package']['profiles']['linux-clang']['expected_size'],manifest['package']['profiles']['linux-clang']['expected_sha256']),(4446156,'2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3'))
 def notify(self,value,action,isr=0,query=1):
  p=ctypes.c_uint32(0xcccccccc);w=ctypes.c_uint32(0);r=self.lib.open_cfw_thread_flags_host_notify(value,action,isr,query,ctypes.byref(p),ctypes.byref(w));return r,p.value,w.value
 def test_all_notify_actions_and_previous_value(self):
  expectations=[(0,0x12),(1,0x17),(2,0x13),(3,0x05),(4,0x05)]
  for action,want in expectations:
   self.reset();self.lib.open_cfw_thread_flags_host_set_target(0x12,0,0);r,p,_=self.notify(5,action);self.assertEqual((r,p,self.get(0),self.get(1)),(1,0x12,want,2))
  self.reset();self.lib.open_cfw_thread_flags_host_set_target(0x12,2,0);r,p,_=self.notify(5,4);self.assertEqual((r,p,self.get(0)),(0,0x12,0x12))
 def test_task_notify_unblocks_ready_resets_and_yields(self):
  self.reset(2,5);self.lib.open_cfw_thread_flags_host_set_target(1,1,1);r,p,_=self.notify(4,1);self.assertEqual((r,p,self.get(0),self.get(8),self.get(9),self.get(7),self.get(6),self.get(11)),(1,1,5,1,1,1,1,5))
  self.reset(6,5);self.lib.open_cfw_thread_flags_host_set_target(1,1,1);self.notify(4,1);self.assertEqual(self.get(6),0)
 def test_from_isr_ready_pending_and_wakeup_contract(self):
  self.reset(2,5);self.lib.open_cfw_thread_flags_host_set_target(1,1,1);r,p,w=self.notify(2,1,1);self.assertEqual((r,p,w,self.get(8),self.get(9),self.get(12),self.get(14),self.get(13)),(1,1,1,1,1,1,1,0x51))
  self.reset(2,5);self.lib.open_cfw_thread_flags_host_set_suspended(1);self.lib.open_cfw_thread_flags_host_set_target(1,1,1);self.notify(2,1,1);self.assertEqual((self.get(8),self.get(9),self.get(10)),(0,0,1))
 def test_kernel_wait_immediate_timeout_and_blocked_notification(self):
  out=ctypes.c_uint32()
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(0x17,2);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_kernel(0,5,9,ctypes.byref(out)),1);self.assertEqual((out.value,self.get(2),self.get(3)),(0x17,0x12,0))
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(0x17,0);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_kernel(7,0,0,ctypes.byref(out)),0);self.assertEqual((out.value,self.get(2),self.get(3)),(0x10,0x10,0))
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(0,0);self.lib.open_cfw_thread_flags_host_set_yield_notification(1,0x21);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_kernel(0,1,10,ctypes.byref(out)),1);self.assertEqual((out.value,self.get(2),self.get(6),self.get(7)),(0x21,0x20,1,1))
 def test_cmsis_set_task_isr_and_validation(self):
  self.reset();self.assertEqual(self.lib.open_cfw_thread_flags_host_set_wrapper(1,1),0xfffffffc);self.assertEqual(self.lib.open_cfw_thread_flags_host_set_wrapper(0,0x80000000),0xfffffffc)
  self.reset();self.lib.open_cfw_thread_flags_host_set_target(0x10,0,0);self.assertEqual(self.lib.open_cfw_thread_flags_host_set_wrapper(0,3),0x13)
  self.reset();self.lib.open_cfw_thread_flags_host_set_irq(1);self.lib.open_cfw_thread_flags_host_set_target(0x10,1,1);self.assertEqual(self.lib.open_cfw_thread_flags_host_set_wrapper(0,3),0x13);self.assertEqual(self.get(16),1)
 def test_cmsis_wait_statuses_options_and_no_repair(self):
  self.reset();self.lib.open_cfw_thread_flags_host_set_irq(1);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_wrapper(1,0,0),0xfffffffa)
  self.reset();self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_wrapper(0x80000000,0,0),0xfffffffc)
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(0,0);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_wrapper(1,0,0),0xfffffffd)
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(0,0);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_wrapper(1,0,3),0xfffffffe)
  self.reset();self.lib.open_cfw_thread_flags_host_set_current(3,2);self.assertEqual(self.lib.open_cfw_thread_flags_host_wait_wrapper(3,2,0),3);self.assertEqual(self.get(2),3)
  self.assertNotIn('open_cfw_freertos_task_notify(',CMSIS.read_text().split('open_cfw_cmsis_thread_flags_wait',1)[1])
if __name__=='__main__':unittest.main()
