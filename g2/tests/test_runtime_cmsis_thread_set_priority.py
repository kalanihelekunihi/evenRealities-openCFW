from __future__ import annotations
import ctypes,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SOURCE=ROOT/'components/shared/freertos/runtime_freertos_task_priority_set.c';HEADER=SOURCE.with_suffix('.h');CMSIS=ROOT/'components/apollo_main/core_overlay/runtime_cmsis_thread_set_priority.c';FIXTURE=ROOT/'tests/fixtures/runtime_cmsis_thread_set_priority_host.c';OFFICIAL=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';OVERLAY=ROOT/'components/apollo_main/core_overlay/overlay.json';MANIFEST=ROOT/'manifests/g2-2.2.6.10-core-source.json'
class RuntimeCmsisThreadSetPriorityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();clang=os.environ.get('OPENCFW_CLANG','/usr/bin/clang');lib=Path(cls.tmp.name)/('p.dylib' if sys.platform=='darwin' else 'p.so');cmd=[clang,'-O2','-Wall','-Wextra','-Werror',str(FIXTURE),'-dynamiclib' if sys.platform=='darwin' else '-shared'];
  if sys.platform!='darwin':cmd.append('-fPIC')
  subprocess.run([*cmd,'-o',str(lib)],check=True,capture_output=True);cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_priority_host_reset.argtypes=[ctypes.c_uint32]*4;cls.lib.open_cfw_priority_host_call.argtypes=[ctypes.c_uint32,ctypes.c_int32];cls.lib.open_cfw_priority_host_call.restype=ctypes.c_int32;cls.lib.open_cfw_priority_host_get.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_priority_host_get.restype=ctypes.c_size_t
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def get(self,n):return self.lib.open_cfw_priority_host_get(n)
 def test_stock_and_sources_are_pinned(self):
  pins=[(SOURCE,3234,'b3e834cab733ce159c09b26c549bc40af5691bc27cbbab9fc6f861ec728f268b'),(HEADER,1996,'a0bd2fdb50a7211b2278e36a8848d56c9c6757f961ef2fa15da84d627d22c610'),(CMSIS,827,'a4d574e941d3669efb2b95bede3fe2bf98c5ba5751fc5d9d63166287c2421a49')]
  for p,s,h in pins:self.assertEqual((p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()),(s,h))
  b=OFFICIAL.read_bytes()[32:];base=0x438000
  for a,z,h in [(0x4491b2,0x4491e4,'076a7d980114be9f392de41e1f1d058cb45a27bb5f6f831c3171c36039c4c388'),(0x454c12,0x454cec,'fa38a23c007a168f79051504b23dd4087eb7845da2c3fb933c8083c8ade31152')]:self.assertEqual(hashlib.sha256(b[a-base:z-base]).hexdigest(),h)
 def test_dual_profile_production_admission_is_pinned(self):
  config=json.loads(OVERLAY.read_text());leaves={x['function']:x for x in config['relocated_leaves']}
  task=leaves['open_cfw_freertos_task_priority_set'];cmsis=leaves['open_cfw_cmsis_thread_set_priority']
  self.assertEqual((task['expected']['size'],task['expected']['offset'],task['expected']['sha256'],task['expected']['unrelocated_sha256']),(208,135396,'eae210caeb12c0fbce18526fea5f5e19fd9be8741d93a0b683b5249fe800e8c6','9ae674f143dcf47f68f6a8168a2dd7eb0d6ac40ff836e740c51332a0859c7267'))
  self.assertEqual((task['toolchain_profiles']['linux-clang']['expected']['size'],task['toolchain_profiles']['linux-clang']['expected']['offset'],task['toolchain_profiles']['linux-clang']['expected']['sha256'],task['toolchain_profiles']['linux-clang']['expected']['unrelocated_sha256']),(210,137272,'16825c343d30bde6b924c2242bb5c3982e800a92fbfd620e3eaf0208c8d54ea0','5dbb2489986faa02c2c9d2c623c7645248c64857eddb4429f68cc7bb84eea9a7'))
  self.assertEqual((cmsis['expected']['size'],cmsis['expected']['offset'],cmsis['expected']['sha256'],cmsis['expected']['unrelocated_sha256']),(50,135604,'e7a9fdfef6ea32076f2a7d9fe1c023185a71681326b21ef7fcf5d8f17717d77c','d5689b9f6710ddad0074ded2e24b6becf30967b532b8e335fa882d78f1ee7e9b'))
  self.assertEqual((cmsis['toolchain_profiles']['linux-clang']['expected']['size'],cmsis['toolchain_profiles']['linux-clang']['expected']['offset'],cmsis['toolchain_profiles']['linux-clang']['expected']['sha256']),(50,137484,'ed2b2474fffee68d71ff02a85eb6ef5ea146c57e8e8b353a7c5801e808e0e1b8'))
  manifest=json.loads(MANIFEST.read_text());main=manifest['component_overrides']['apollo_main'];regions={x['name']:x for x in main['regions']}
  self.assertEqual((regions['apollo_freertos_task_priority_set_source_leaf']['file_offset'],regions['apollo_freertos_task_priority_set_source_leaf']['size'],regions['apollo_freertos_task_priority_set_source_leaf']['target_address']),(3658792,208,8082440))
  self.assertEqual((regions['apollo_cmsis_thread_set_priority_source_leaf']['file_offset'],regions['apollo_cmsis_thread_set_priority_source_leaf']['size'],regions['apollo_cmsis_thread_set_priority_source_leaf']['target_address']),(3659000,50,8082648))
  self.assertEqual((main['provider']['size'],main['provider']['profiles']['linux-clang']['size']),(3688808,3668576))
  self.assertEqual((manifest['package']['expected_size'],manifest['package']['expected_sha256']),(4467302,'88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f'))
  self.assertEqual((manifest['package']['profiles']['linux-clang']['expected_size'],manifest['package']['profiles']['linux-clang']['expected_sha256']),(4447070,'be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25'))
 def test_raise_ready_task_moves_list_and_yields(self):
  self.lib.open_cfw_priority_host_reset(10,5,5,1);self.assertEqual(self.lib.open_cfw_priority_host_call(0,12),0);self.assertEqual(tuple(self.get(i) for i in range(7)),(12,12,44,1,12,1,1))
 def test_inherited_priority_changes_base_only(self):
  self.lib.open_cfw_priority_host_reset(20,15,7,0);self.assertEqual(self.lib.open_cfw_priority_host_call(0,9),0);self.assertEqual((self.get(0),self.get(1)),(15,9))
 def test_current_lower_yields_and_wrapper_validates(self):
  self.lib.open_cfw_priority_host_reset(20,5,5,0);self.assertEqual(self.lib.open_cfw_priority_host_call(1,8),0);self.assertEqual((self.get(9),self.get(10),self.get(5)),(8,8,1));self.assertEqual(self.lib.open_cfw_priority_host_call(0,0),-4);self.lib.open_cfw_priority_host_set_irq(1);self.assertEqual(self.lib.open_cfw_priority_host_call(0,8),-6)
if __name__=='__main__':unittest.main()
