#!/usr/bin/env python3
from __future__ import annotations
import ctypes,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'components/shared/lvgl/runtime_ambiq_gpu_patch_bitmap_glyph_candidate.c';F=ROOT/'tests/fixtures/runtime_ambiq_gpu_patch_bitmap_glyph_candidate_host.c';M=ROOT/'tools/manifests/g2-nemagfx-ambiq-provenance.json';A=ROOT/'docs/research/ambiq-gpu-patch-bitmap-glyph-source-candidate-audit.md';FLAGS=['--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-mfloat-abi=hard','-std=c11','-O2','-ffreestanding','-ffunction-sections','-fdata-sections','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror']
class G(ctypes.Structure):_fields_=[('bitmap',ctypes.c_void_p),('bitmap_width',ctypes.c_uint32),('bitmap_height',ctypes.c_uint32),('raster_x',ctypes.c_int32),('raster_y',ctypes.c_int32),('raster_width',ctypes.c_uint32),('raster_height',ctypes.c_uint32),('format',ctypes.c_uint32),('color',ctypes.c_uint32),('stride',ctypes.c_uint32),('rotate_angle',ctypes.c_int32),('pivot_x',ctypes.c_int32),('pivot_y',ctypes.c_int32),('temporary_used',ctypes.c_bool),('temporary',ctypes.c_void_p),('temporary_width',ctypes.c_uint32),('temporary_height',ctypes.c_uint32),('temporary_format',ctypes.c_uint32),('temporary_stride',ctypes.c_uint32)]
class T(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.cl=os.environ.get('OPENCFW_CLANG')or shutil.which('clang');c.tmp=tempfile.TemporaryDirectory(prefix='glyph-');p=Path(c.tmp.name);lib=p/('g.dylib'if sys.platform=='darwin'else'g.so');subprocess.run([c.cl,'-O2','-Wall','-Wextra','-Werror',str(S),str(F),*(['-dynamiclib']if sys.platform=='darwin'else['-shared','-fPIC']),'-o',str(lib)],check=True,cwd=ROOT,capture_output=True,text=True);c.l=ctypes.CDLL(str(lib));c.l.test_glyph_run.argtypes=[ctypes.POINTER(G)];c.l.test_glyph_count.restype=ctypes.c_uint32;c.l.test_glyph_op.argtypes=[ctypes.c_uint32];c.l.test_glyph_op.restype=ctypes.c_uint32;c.l.test_glyph_arg.argtypes=[ctypes.c_uint32]*2;c.l.test_glyph_arg.restype=ctypes.c_uint64;c.l.test_glyph_float.argtypes=[ctypes.c_uint32]*2;c.l.test_glyph_float.restype=ctypes.c_float;c.o=p/'g.o';subprocess.run([c.cl,*FLAGS,'-c',str(S),'-o',str(c.o)],check=True,cwd=ROOT,capture_output=True,text=True)
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def trace(s,g):s.l.test_glyph_run(ctypes.byref(g));return[s.l.test_glyph_op(i)for i in range(s.l.test_glyph_count())]
 def ar(s,i):return tuple(s.l.test_glyph_arg(i,a)for a in range(7))
 def fl(s,i):return tuple(s.l.test_glyph_float(i,a)for a in range(9))
 def base(s,**kw):
  d=dict(bitmap=0x1000,bitmap_width=8,bitmap_height=5,raster_x=2,raster_y=3,raster_width=7,raster_height=4,format=0x34,color=0xff112233,stride=4,rotate_angle=0,pivot_x=1,pivot_y=2,temporary_used=False,temporary=0x2000,temporary_width=64,temporary_height=16,temporary_format=8,temporary_stride=64);d.update(kw);return G(**d)
 def test_direct(s):
  o=s.trace(s.base());s.assertEqual(o,[1,5,6,8,9,11,14]);s.assertEqual(s.ar(0)[:6],(0x1000,8,5,0x34,4,0));s.assertEqual(s.fl(2)[:2],(2,3));s.assertEqual(s.ar(6)[:4],(2,3,7,4))
 def test_one_line(s):
  o=s.trace(s.base(bitmap_width=7,bitmap_height=5,format=0x0c,stride=0));s.assertEqual(o,[1,5,11,14]);s.assertEqual(s.ar(0)[:6],(0x1000,35,1,0x0c,0,0));s.assertEqual(s.fl(2)[:3],(1,7,-26.5))
 def test_temp_chunk_and_nonopaque(s):
  g=s.base(bitmap_width=7,bitmap_height=400,format=0x0c,stride=0,rotate_angle=0,color=0x80112233);o=s.trace(g);s.assertTrue(g.temporary_used);s.assertEqual(o[:4],[2,3,4,5]);binds=[i for i,x in enumerate(o)if x==2];s.assertEqual([s.ar(i)[2]for i in binds],[64,2044,784]);s.assertEqual(s.ar(binds[2])[1],0x1000+252);s.assertIn(12,o);s.assertIn(13,o);s.assertEqual(next(s.ar(i)[0]for i,x in enumerate(o)if x==3 and i>1),0x08000504)
 def test_rotated_quad(s):
  o=s.trace(s.base(rotate_angle=3610));s.assertIn(7,o);s.assertEqual(s.fl(o.index(7))[0],1.0);s.assertEqual(o[-1],15)
 def test_manifest(s):
  p=json.loads(M.read_text());x=next(x for x in p['gpu_patch']['binary_recovery']['function_census']if x['function']=='lv_ambiq_draw_bitmap_glyph');s.assertEqual((x['section_size'],x['section_sha256'],x['source_line'],x['relocation_count']),(1036,'37ad8ca8a082a00d04feae707022535448d1920940335db4819130901c47f0a1',590,34));s.assertEqual(x['source_status'],'bounded-clean-room-candidate')
 def test_target(s):
  sys.path.insert(0,str(ROOT/'tools'));import apollo_overlay
  _,q=apollo_overlay.parse_elf32(s.o);t={int(x['index'])for x in q if str(x['name']).startswith('.text.')and int(x['size'])};s.assertEqual([x for x in q if int(x['type'])==9 and int(x['size'])and int(x['info'])in t],[])
 def test_independent(s):s.assertNotIn('void lv_ambiq_draw_bitmap_glyph(',S.read_text());s.assertIn('four rendering paths',A.read_text())
if __name__=='__main__':unittest.main()
