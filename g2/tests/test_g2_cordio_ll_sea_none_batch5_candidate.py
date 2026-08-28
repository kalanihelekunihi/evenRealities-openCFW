#!/usr/bin/env python3
from __future__ import annotations
import ctypes,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch5_candidate.py";SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch5/runtime_cordio_ll_sea_none_batch5_candidate.c"
def load_analyzer():
 s=importlib.util.spec_from_file_location("none_batch5",ANALYZER)
 if s is None or s.loader is None:raise RuntimeError("load failed")
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Evidence(ctypes.Structure):_fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure):_fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))
class NoneBatch5Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
  if cc is None:raise unittest.SkipTest("no compiler")
  cls.temp=tempfile.TemporaryDirectory(prefix="none5-");lib=Path(cls.temp.name)/"libnone5.so";subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch5_evidence_count.restype=ctypes.c_size_t;cls.lib.open_cfw_cordio_ll_sea_none_batch5_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch5_evidence.restype=ctypes.POINTER(Evidence);cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch5_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_chained_partition(self):
  d=self.analyzer.run_audit();self.assertEqual(d["status"],"candidate-qualified-none-batch5");self.assertEqual(d["none_group"]["batch5_source_recovered"],{"functions":7,"bytes":1010});self.assertEqual(d["none_group"]["upstream_freetype_source"],{"functions":84,"bytes":10854});self.assertEqual(d["none_group"]["typed_external"],{"functions":114,"bytes":22790});self.assertEqual(d["unsupported_remainder"]["before"],{"functions":121,"bytes":23800});self.assertFalse(d["adapter"]["production_routed"])
 def test_table(self):
  self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch5_evidence_count(),7);total=0
  for i in range(7):
   x=self.lib.open_cfw_cordio_ll_sea_none_batch5_evidence(i).contents;total+=x.size;self.assertEqual(x.end-x.start,x.size);self.assertIn(x.module,(b"pstables.h",b"psmodule.c"));self.assertIn(b"FreeType Project License",x.license)
  self.assertEqual(total,1010);self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch5_evidence(7))
 def test_exact_and_gap_guard(self):
  d=self.analyzer.run_audit();r=d["none_group"]["records"];self.assertEqual(r["0x005D94C0"]["upstream_function"],"ft_get_adobe_glyph_index");self.assertEqual(r["0x005D9716"]["upstream_function"],"ps_unicodes_init");self.assertEqual(r["0x005D9890"]["upstream_function"],"ps_unicodes_char_next");self.assertEqual(r["0x005D9950"]["disposition"],"typed_external");self.assertEqual(d["uncatalogued_gap"]["bytes"],68);self.assertFalse(d["uncatalogued_gap"]["claimed_exact"])
 def test_provider_fail_closed(self):
  calls=[]
  @PROVIDER
  def provider(_c,m,f,i):calls.append((m.decode(),f.decode()));i.contents.words[0]=17;return 0
  inv=Invocation();self.assertEqual(self.invoke(0x005D9840,provider,None,ctypes.byref(inv)),0);self.assertEqual(calls,[("psmodule.c","ps_unicodes_char_index")]);self.assertEqual(self.invoke(0x005D9672,provider,None,ctypes.byref(inv)),2);self.assertEqual(self.invoke(0x005D9840,PROVIDER(),None,ctypes.byref(inv)),3);self.assertEqual(self.invoke(0x005D9840,provider,None,None),1)
 def test_cli_deterministic(self):
  c=[sys.executable,str(ANALYZER)];a=subprocess.run(c,check=True,capture_output=True,text=True).stdout;b=subprocess.run(c,check=True,capture_output=True,text=True).stdout;self.assertEqual(a,b);self.assertEqual(json.loads(a)["status"],"candidate-qualified-none-batch5")
if __name__=="__main__":unittest.main()
