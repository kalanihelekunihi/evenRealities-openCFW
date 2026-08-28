from __future__ import annotations
import ctypes,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/shared/freertos/runtime_freertos_task_delete.c';HEADER=SOURCE.with_suffix('.h');CMSIS=ROOT/'components/apollo_main/core_overlay/runtime_cmsis_thread_terminate.c';FIXTURE=ROOT/'tests/fixtures/runtime_cmsis_thread_terminate_host.c';OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
class RuntimeCmsisThreadTerminateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();clang=os.environ.get('OPENCFW_CLANG','/usr/bin/clang');lib=Path(cls.tmp.name)/('t.dylib' if sys.platform=='darwin' else 't.so');cmd=[clang,'-O2','-Wall','-Wextra','-Werror',str(FIXTURE),'-dynamiclib' if sys.platform=='darwin' else '-shared'];
  if sys.platform!='darwin':cmd.append('-fPIC')
  subprocess.run([*cmd,'-o',str(lib)],check=True,capture_output=True);cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_terminate_host_reset.argtypes=[ctypes.c_uint32]*4;cls.lib.open_cfw_terminate_host_state.restype=ctypes.c_int32;cls.lib.open_cfw_terminate_host_delete.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_terminate_host_wrapper.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_terminate_host_wrapper.restype=ctypes.c_int32;cls.lib.open_cfw_terminate_host_set_irq.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_terminate_host_set_suspended.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_terminate_host_get.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_terminate_host_get.restype=ctypes.c_size_t
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def reset(self,*args):self.lib.open_cfw_terminate_host_reset(*args)
 def get(self,n):return self.lib.open_cfw_terminate_host_get(n)
 def test_stock_and_sources_are_pinned(self):
  pins=[(SOURCE,4684,'fd0f9a420781d8bcf2365bae20a5b6946e6092a33bb7ea8bf713f3ab9e5261cd'),(HEADER,5848,'2a6d6caf1725649f269c25a03df6197afae15a8d8575b097d7112b924112ef17'),(CMSIS,824,'f4c5d8ead302418dfc0009fd2b1351107c4bdb7c95a37b27cd4dd2ed4b7d58cd')]
  for p,s,h in pins:self.assertEqual((p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()),(s,h))
  b=OFFICIAL.read_bytes()[32:];base=0x438000
  spans=[(0x4491fe,0x449238,'d89f27dd18cbf97e9e82e793f812b6354b85d56f125220edb8cec9ae6993adc2'),(0x454aae,0x454b4c,'fed4eb28935bf7034f3f1893518e7de056995a5083d42863ab007e9e74de2597'),(0x454b88,0x454c12,'e4781094cbfded3f125a131f0d793cc67b47af6db0f879036d0ca6afc1056bfc'),(0x455836,0x455876,'86f7fc5725fe0fbbe85c07f68669981bad154cd58163427a6ead8106538e2a12')]
  for a,z,h in spans:self.assertEqual(hashlib.sha256(b[a-base:z-base]).hexdigest(),h)
 def test_dual_profile_production_admission_is_pinned(self):
  config=json.loads(OVERLAY.read_text());leaves={x['function']:x for x in config['relocated_leaves']}
  pins={'open_cfw_freertos_task_get_state':((142,195504,'99dc8c3853bc6dadaf1136e76278c061c617b1cdf7bbee9a8571203bd8fd2cec'),(142,197288,'1a3f930365324ae342ecafee903cf516db609a389c22fa6722a285232947a603')),'open_cfw_freertos_task_delete_tcb':((58,195648,'4c507c8b61d1e23140ed5537d5dc5adfdffcbbec0c2c696e2f37e511a8994bb3'),(58,197432,'8dfa50c7052839f23e89184c2de1437fcecee73ef13ed6273728abeb6105ea84')),'open_cfw_freertos_task_delete':((152,195708,'f95981b3779d66b0705a1d7acd380fe8bf2eea33246f75176c9b41f4f3bc8f5a'),(152,197492,'c168feddb95a750c06b89d1729e320887f1d56c43c31eee97456104b47222a5a')),'open_cfw_cmsis_thread_terminate':((52,195860,'eeeaeda0130b62e7a4c02afc6ed1909f7b7afa32506a8e93bb491cc840ab55c8'),(52,197644,'cec3e962cbc2978a891e4299f959b6945b3395814d118f42533f8b64c4d65db9'))}
  for name,(apple,linux) in pins.items():
   leaf=leaves[name];self.assertEqual((leaf['expected']['size'],leaf['expected']['offset'],leaf['expected']['sha256']),apple);p=leaf['toolchain_profiles']['linux-clang']['expected'];self.assertEqual((p['size'],p['offset'],p['sha256']),linux);self.assertTrue(leaf['strict_relocation_contract'])
  manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions={x['name']:x for x in main['regions']}
  self.assertEqual((regions['apollo_freertos_task_get_state_source_leaf']['file_offset'],regions['apollo_freertos_task_delete_tcb_source_leaf']['file_offset'],regions['apollo_freertos_task_delete_source_leaf']['file_offset'],regions['apollo_cmsis_thread_terminate_source_leaf']['file_offset']),(3718900,3719044,3719104,3719256))
  self.assertEqual((main['provider']['size'],main['provider']['profiles']['linux-clang']['size']),(3952454,3736060));self.assertEqual((manifest['package']['expected_size'],manifest['package']['expected_sha256']),(4745526,'4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934'));self.assertEqual((manifest['package']['profiles']['linux-clang']['expected_size'],manifest['package']['profiles']['linux-clang']['expected_sha256']),(4529116,'f0526433c366a85ab79e27df6d28ffc70d6a2ed93e608652885b49b404e380ef'))
 def test_state_classification(self):
  expected={0:1,1:2,2:2,3:3,4:2,5:2,6:4,7:4}
  for mode,state in expected.items():self.reset(mode,0,2,0);self.assertEqual(self.lib.open_cfw_terminate_host_state(),state)
  self.reset(1,1,2,0);self.assertEqual(self.lib.open_cfw_terminate_host_state(),0)
 def test_noncurrent_delete_removes_frees_and_resets(self):
  self.reset(4,0,0,1);self.lib.open_cfw_terminate_host_delete(0);self.assertEqual(tuple(self.get(i) for i in range(13)),(1,1,1,1,0,1,1,1,0,0,4,1,10))
  self.reset(0,0,1,0);self.lib.open_cfw_terminate_host_delete(0);self.assertEqual((self.get(6),self.get(7)),(0,1))
  self.reset(0,0,2,0);self.lib.open_cfw_terminate_host_delete(0);self.assertEqual((self.get(6),self.get(7),self.get(9)),(0,0,0))
 def test_current_delete_defers_cleanup_and_yields(self):
  self.reset(0,1,0,1);self.lib.open_cfw_terminate_host_delete(1);self.assertEqual(tuple(self.get(i) for i in (2,4,5,6,7,8,10,11,12,13)),(1,1,0,0,0,1,5,2,10,1))
  self.reset(0,1,0,1);self.lib.open_cfw_terminate_host_set_suspended(1);self.lib.open_cfw_terminate_host_delete(0);self.assertEqual((self.get(8),self.get(9)),(1,1))
 def test_wrapper_validation_deleted_and_success(self):
  self.reset(0,0,2,0);self.lib.open_cfw_terminate_host_set_irq(1);self.assertEqual(self.lib.open_cfw_terminate_host_wrapper(0),-6);self.lib.open_cfw_terminate_host_set_irq(0);self.assertEqual(self.lib.open_cfw_terminate_host_wrapper(1),-4)
  self.reset(6,0,2,0);self.assertEqual(self.lib.open_cfw_terminate_host_wrapper(0),-3);self.assertEqual(self.get(2),0)
  self.reset(0,0,2,0);self.assertEqual(self.lib.open_cfw_terminate_host_wrapper(0),0);self.assertEqual(self.get(2),1)
if __name__=='__main__':unittest.main()
