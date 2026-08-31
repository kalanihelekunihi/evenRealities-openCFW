#!/usr/bin/env python3
"""Qualify the corner-mask and L8/L4 clean-room candidates."""

from __future__ import annotations
import ctypes,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/shared/lvgl/runtime_ambiq_gpu_patch_small_raster_candidate.c"
FIXTURE=ROOT/"tests/fixtures/runtime_ambiq_gpu_patch_small_raster_candidate_host.c"
MANIFEST=ROOT/"tools/manifests/g2-nemagfx-ambiq-provenance.json"
AUDIT=ROOT/"docs/research/ambiq-gpu-patch-small-raster-source-candidate-audit.md"
TARGET_FLAGS=["--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-mfloat-abi=hard","-std=c11","-O2","-ffreestanding","-ffunction-sections","-fdata-sections","-fno-builtin","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror"]

class SmallRasterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.clang=os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
  if not cls.clang: raise unittest.SkipTest("clang unavailable")
  cls.temp=tempfile.TemporaryDirectory(prefix="opencfw-small-raster-");t=Path(cls.temp.name);lib=t/("small.dylib" if sys.platform=="darwin" else "small.so")
  subprocess.run([cls.clang,"-O2","-Wall","-Wextra","-Werror",str(SOURCE),str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(lib)],check=True,cwd=ROOT,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_test_small_corner.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_size_t];cls.lib.open_cfw_test_small_convert.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.c_size_t,ctypes.c_size_t];cls.lib.open_cfw_test_small_convert.restype=ctypes.c_uint32
  cls.lib.open_cfw_test_small_count.restype=ctypes.c_uint32;cls.lib.open_cfw_test_small_operation.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_test_small_operation.restype=ctypes.c_uint32;cls.lib.open_cfw_test_small_argument.argtypes=[ctypes.c_uint32]*2;cls.lib.open_cfw_test_small_argument.restype=ctypes.c_uint64;cls.lib.open_cfw_test_small_value.argtypes=[ctypes.c_uint32]*2;cls.lib.open_cfw_test_small_value.restype=ctypes.c_float
  cls.target=t/"small.o";subprocess.run([cls.clang,*TARGET_FLAGS,"-c",str(SOURCE),"-o",str(cls.target)],check=True,cwd=ROOT,capture_output=True,text=True)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def ops(self):return [self.lib.open_cfw_test_small_operation(i) for i in range(self.lib.open_cfw_test_small_count())]
 def args(self,i):return tuple(self.lib.open_cfw_test_small_argument(i,a) for a in range(7))
 def vals(self,i):return tuple(self.lib.open_cfw_test_small_value(i,a) for a in range(9))
 def test_corner_exact_effects(self):
  self.lib.open_cfw_test_small_corner(20,6,0x12340000);self.assertEqual(self.ops(),[1,2,3,4,5,3,6,4,7,8]);self.assertEqual(self.args(0),(1,0x12340000,20,20,8,0xffffffff,0));self.assertEqual(self.args(1)[:4],(1,1,0xffffffff,0xffffffff));self.assertEqual(self.args(5)[:4],(0,6,14,20));self.assertEqual(self.args(6)[:5],(255,255,255,255,0xffffffff));self.assertEqual(self.vals(8)[:6],(0,20,0,14,270,360))
 def test_convert_even_exact_pipeline(self):
  self.assertEqual(self.lib.open_cfw_test_small_convert(12,7,0x1000,0x2000),0);self.assertEqual(self.ops(),[1,3,1,9,10,2,11,5,1,9,10,2,12,5,8]);self.assertEqual(self.args(0),(2,0x2000,6,7,0x45,6,0));self.assertEqual(self.args(2),(1,0x1000,24,7,0x34,12,0));self.assertEqual(self.vals(4),(4,0,-2,0,1,0,0,0,1));self.assertEqual(self.args(5)[:4],(1,2,1,0xffffffff));self.assertEqual(self.args(8),(1,0x1000,24,7,0x35,12,0));self.assertEqual(self.vals(10),(4,0,0,0,1,0,0,0,1));self.assertEqual(self.args(11)[:4],(0x10000101,2,1,0xffffffff))
 def test_convert_odd_is_noop(self):self.assertEqual(self.lib.open_cfw_test_small_convert(11,7,1,2),0);self.assertEqual(self.ops(),[])
 def test_manifest_sections_and_statuses(self):
  p=json.loads(MANIFEST.read_text());c={x['function']:x for x in p['gpu_patch']['binary_recovery']['function_census']};self.assertEqual((c['lv_ambiq_create_corner_mask']['section_size'],c['lv_ambiq_create_corner_mask']['section_sha256']),(164,'6b1cbd72576ee8310eb7eab466570e6daa51a9446696ea8e748eea0088e0f95c'));self.assertEqual((c['lv_ambiq_l8_l4_convert']['section_size'],c['lv_ambiq_l8_l4_convert']['section_sha256']),(224,'180127efa5ccd439952423bbd6dbde4123c59c574fd367f0c808a37ea0643bbe'));self.assertEqual(c['lv_ambiq_create_corner_mask']['source_status'],'bounded-clean-room-candidate');self.assertEqual(c['lv_ambiq_l8_l4_convert']['source_status'],'bounded-clean-room-candidate')
 def test_target_text_is_external_relocation_free(self):
  sys.path.insert(0,str(ROOT/'tools'));import apollo_overlay
  _,s=apollo_overlay.parse_elf32(self.target);texts={int(x['index']) for x in s if str(x['name']).startswith('.text.') and int(x['size'])};rels=[x for x in s if int(x['type'])==9 and int(x['size']) and int(x['info']) in texts];self.assertEqual(rels,[])
 def test_independent_documented_production_excluded(self):
  t=SOURCE.read_text();self.assertIn('SPDX-License-Identifier: MIT',t);self.assertNotIn('GPL-3.0-only',t);self.assertNotIn('void lv_ambiq_create_corner_mask(',t);self.assertIn('two non-required',AUDIT.read_text());production='\n'.join((ROOT/x).read_text(errors='replace') for x in ['components/apollo_main/core_overlay/overlay.json','manifests/g2-2.2.6.10-core-source.json']);self.assertNotIn('open_cfw_ambiq_gpu_create_corner_mask_candidate',production)

if __name__=='__main__':unittest.main()
