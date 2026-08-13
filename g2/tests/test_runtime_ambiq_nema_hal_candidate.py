#!/usr/bin/env python3
from __future__ import annotations
import ctypes, importlib.util, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_nema_hal_candidate.c"
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_nema_hal_candidate_host.c"
AUDIT = ROOT / "docs/research/ambiq-nema-bare-metal-hal-source-candidate-audit.md"
ANALYZER = ROOT / "tools/analyze_g2_nema_hal.py"

class NemaHalCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.clang=os.environ.get("OPENCFW_CLANG") or shutil.which("clang"); cls.tmp=tempfile.TemporaryDirectory(prefix="nema-hal-"); p=Path(cls.tmp.name); lib=p/("h.dylib" if sys.platform=="darwin" else "h.so")
  subprocess.run([cls.clang,"-O2","-Wall","-Wextra","-Werror",str(SOURCE),str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(lib)],check=True,cwd=ROOT,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib)); cls.lib.test_nema_hal_create.argtypes=[ctypes.c_int32,ctypes.c_uint32];cls.lib.test_nema_hal_create.restype=ctypes.c_uint64;cls.lib.test_nema_hal_arg.restype=ctypes.c_uint64
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def reset(self,*flags): self.lib.test_nema_hal_reset(*flags)
 def ops(self): return [self.lib.test_nema_hal_op(i) for i in range(self.lib.test_nema_hal_count())]
 def test_pool_selection_alignment_and_rounding(self):
  self.reset(0,0,0); value=self.lib.test_nema_hal_create(0,33);self.assertEqual((value>>32,value&0xffffffff),(33,0));self.assertEqual(self.lib.test_nema_hal_b(0),33);self.assertEqual(self.lib.test_nema_hal_c(0),8)
  self.reset(0,1,0); value=self.lib.test_nema_hal_create(2,33);self.assertEqual(value>>32,64);self.assertEqual(self.lib.test_nema_hal_c(0),32)
  self.reset(0,0,0);self.lib.test_nema_hal_create(3,33);self.assertEqual(self.lib.test_nema_hal_c(0),0)
 def test_pool_bounds_and_default_render_mapping(self):
  self.reset(0,0,0);self.assertEqual(self.lib.test_nema_hal_within(2,0x60000100,0x100),1);self.assertEqual(self.lib.test_nema_hal_within(2,0x5fffffff,1),0);self.assertEqual(self.lib.test_nema_hal_within(99,0x20010000,0x1000),1)
 def test_sys_init_exact_ring_irq_and_semaphore_contract(self):
  self.reset(0,0,0);self.assertEqual(self.lib.test_nema_hal_sys_init(),0);self.assertEqual(self.lib.test_nema_hal_ring_size(),0x1300);self.assertEqual(self.lib.test_nema_hal_ring_fd(),0);self.assertEqual(self.lib.test_nema_hal_last(),-1);self.assertEqual(self.ops(),[11,10,5,1,6]);self.assertEqual((self.lib.test_nema_hal_arg(0),self.lib.test_nema_hal_b(0)),(28,4));self.assertEqual((self.lib.test_nema_hal_arg(2),self.lib.test_nema_hal_b(2),self.lib.test_nema_hal_c(2)),(1,0,3))
 def test_irq_loop_publication_release_and_callback(self):
  self.reset(0,0,0);self.lib.test_nema_hal_sys_init();before=self.lib.test_nema_hal_count();self.lib.test_nema_hal_irq(17);ops=self.ops()[before:];self.assertEqual(ops,[9,4,12,13]);self.assertEqual(self.lib.test_nema_hal_last(),17)
 def test_exact_stock_census_and_public_lineage(self):
  spec=importlib.util.spec_from_file_location("nema_hal_audit",ANALYZER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);report=module.analyze();stock=report["stock"];self.assertEqual((stock["function_count"],stock["bytes"],stock["direct_bl_call_sites"]),(18,614,83));self.assertEqual((stock["gpu_base"],stock["irq"],stock["ring_bytes"],stock["max_pending_command_lists"]),(0x40090000,28,0x1300,100));self.assertIsNone(report["public_lineage"]["stock_generating_source"])
 def test_analyzer_rejects_a_mutated_stock_hal_cluster(self):
  spec=importlib.util.spec_from_file_location("nema_hal_mutation_audit",ANALYZER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  mutated=bytearray(module.IMAGE.read_bytes());mutated[module.FUNCTIONS[0][1]-module.BASE]^=1;path=Path(self.tmp.name)/"mutated-g2.bin";path.write_bytes(mutated)
  with self.assertRaisesRegex(module.AuditError,"official G2 image changed"):
   module.analyze(path)
 def test_candidate_is_independent_documented_and_target_compiles(self):
  self.assertNotIn("int32_t nema_sys_init(",SOURCE.read_text());self.assertIn("Zephyr",AUDIT.read_text());obj=Path(self.tmp.name)/"hal.o";subprocess.run([self.clang,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-mfloat-abi=hard","-std=c11","-O2","-ffreestanding","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True,cwd=ROOT,capture_output=True,text=True)

if __name__ == "__main__": unittest.main()
