#!/usr/bin/env python3
from __future__ import annotations
import ctypes,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/shared/lvgl/runtime_ambiq_gpu_patch_shadow_blur_vg_candidate.c';FIXTURE=ROOT/'tests/fixtures/runtime_ambiq_gpu_patch_shadow_blur_vg_candidate_host.c';MANIFEST=ROOT/'tools/manifests/g2-nemagfx-ambiq-provenance.json';AUDIT=ROOT/'docs/research/ambiq-gpu-patch-shadow-blur-vg-source-candidate-audit.md';FLAGS=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfloat-abi=hard','-std=c11','-O2','-ffreestanding','-ffunction-sections','-fdata-sections','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror']
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.clang=os.environ.get('OPENCFW_CLANG') or shutil.which('clang');c.t=tempfile.TemporaryDirectory(prefix='opencfw-vg-shadow-');p=Path(c.t.name);lib=p/('vg.dylib' if sys.platform=='darwin' else 'vg.so');subprocess.run([c.clang,'-O2','-Wall','-Wextra','-Werror',str(SOURCE),str(FIXTURE),*(['-dynamiclib']if sys.platform=='darwin'else['-shared','-fPIC']),'-o',str(lib)],check=True,cwd=ROOT,capture_output=True,text=True);c.l=ctypes.CDLL(str(lib));c.l.open_cfw_test_vg_run.argtypes=[ctypes.c_float,ctypes.c_float]+[ctypes.c_size_t]*3;c.l.open_cfw_test_vg_count.restype=ctypes.c_uint32;c.l.open_cfw_test_vg_op.argtypes=[ctypes.c_uint32];c.l.open_cfw_test_vg_op.restype=ctypes.c_uint32;c.l.open_cfw_test_vg_arg.argtypes=[ctypes.c_uint32]*2;c.l.open_cfw_test_vg_arg.restype=ctypes.c_uint64;c.l.open_cfw_test_vg_float.argtypes=[ctypes.c_uint32]*2;c.l.open_cfw_test_vg_float.restype=ctypes.c_float;c.o=p/'vg.o';subprocess.run([c.clang,*FLAGS,'-c',str(SOURCE),'-o',str(c.o)],check=True,cwd=ROOT,capture_output=True,text=True)
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def ops(s):return[s.l.open_cfw_test_vg_op(i)for i in range(s.l.open_cfw_test_vg_count())]
 def args(s,i):return tuple(s.l.open_cfw_test_vg_arg(i,a)for a in range(7))
 def fs(s,i):return tuple(s.l.open_cfw_test_vg_float(i,a)for a in range(12))
 def test_trace(s):
  s.l.open_cfw_test_vg_run(32.5,4,0x1000,0x2000,0x3000);s.assertEqual(s.ops(),[1,2,3,4,5,6,7,8,9,10,11,12,2,4]);s.assertEqual(s.args(1),(0,0x1000,32,32,9,0xffffffff,0));s.assertEqual(s.args(2)[:4],(1,0,0xffffffff,0xffffffff));s.assertEqual(s.args(3)[:4],(0,0,32,32));s.assertEqual(s.args(5)[:4],(0,0,32,32));s.assertAlmostEqual(s.fs(8)[0],1-4/32.5,places=6);s.assertEqual(s.fs(8)[1:10],(1,255,255,255,0,0,0,0,0));s.assertEqual(s.args(9)[:2],(0x2000,3));s.assertEqual(s.args(10)[:3],(0x2000,0x3000,1));s.assertEqual(s.fs(10)[:3],(0,32.5,32.5));s.assertEqual(s.args(11)[:2],(0,0x2000));s.assertEqual(s.args(12),(0,0x12345000,70,80,0x22,0x00ab0090,0xab));s.assertEqual(s.args(13)[:4],(3,4,50,60))
 def test_manifest(s):
  p=json.loads(MANIFEST.read_text());x=next(x for x in p['gpu_patch']['binary_recovery']['function_census']if x['function']=='lv_ambiq_shadow_blur_corner_vg');s.assertEqual((x['section_size'],x['section_sha256'],x['source_line'],x['relocation_count']),(324,'a600d42433a84fe56934d36b167177bf1c617ce3cb8fafcbfecb9ca1948b9974',454,15));s.assertEqual(x['source_status'],'bounded-clean-room-candidate')
 def test_no_text_relocations(s):
  sys.path.insert(0,str(ROOT/'tools'));import apollo_overlay
  _,q=apollo_overlay.parse_elf32(s.o);t={int(x['index'])for x in q if str(x['name']).startswith('.text.')and int(x['size'])};s.assertEqual([x for x in q if int(x['type'])==9 and int(x['size'])and int(x['info'])in t],[])
 def test_independent(s):s.assertNotIn('void lv_ambiq_shadow_blur_corner_vg(',SOURCE.read_text());s.assertIn('context restore',AUDIT.read_text())
if __name__=='__main__':unittest.main()
