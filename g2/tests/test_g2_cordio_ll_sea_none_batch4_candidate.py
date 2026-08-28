#!/usr/bin/env python3
from __future__ import annotations
import ctypes,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch4_candidate.py";SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch4/runtime_cordio_ll_sea_none_batch4_candidate.c"
def load_analyzer():
 s=importlib.util.spec_from_file_location("none_batch4",ANALYZER)
 if s is None or s.loader is None:raise RuntimeError("load failed")
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Evidence(ctypes.Structure):_fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure):_fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))
class NoneBatch4Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
  if cc is None:raise unittest.SkipTest("no compiler")
  cls.temp=tempfile.TemporaryDirectory(prefix="none4-");lib=Path(cls.temp.name)/"libnone4.so"
  subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch4_evidence_count.restype=ctypes.c_size_t;cls.lib.open_cfw_cordio_ll_sea_none_batch4_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch4_evidence.restype=ctypes.POINTER(Evidence)
  cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch4_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_chained_partition(self):
  d=self.analyzer.run_audit();self.assertEqual(d["status"],"candidate-qualified-none-batch4");self.assertEqual(d["none_group"]["batch4_source_recovered"],{"functions":33,"bytes":2124});self.assertEqual(d["none_group"]["upstream_freetype_source"],{"functions":77,"bytes":9844});self.assertEqual(d["none_group"]["typed_external"],{"functions":121,"bytes":23800});self.assertEqual(d["unsupported_remainder"]["before"],{"functions":154,"bytes":25924});self.assertFalse(d["adapter"]["production_routed"])
 def test_table_and_complete_source_order(self):
  self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch4_evidence_count(),33);names=[];total=0
  for i in range(33):
   x=self.lib.open_cfw_cordio_ll_sea_none_batch4_evidence(i).contents;names.append(x.function.decode());total+=x.size;self.assertEqual(x.end-x.start,x.size);self.assertEqual(x.module,b"pshrec.c");self.assertIn(b"FreeType Project License",x.license)
  omitted={g[2] for g in self.analyzer.GAPS};self.assertEqual(tuple(names),tuple(n for n in self.analyzer.FULL_ORDER if n not in omitted));self.assertEqual(total,2124);self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch4_evidence(33))
 def test_representatives_and_uncatalogued_guards(self):
  d=self.analyzer.run_audit();r=d["none_group"]["records"];self.assertEqual(r["0x005D8D44"]["upstream_function"],"ps_mask_table_set_bits");self.assertEqual(r["0x005D8FAE"]["upstream_function"],"ps_dimension_add_t1stem");self.assertEqual(r["0x005D9462"]["upstream_function"],"t2_hints_funcs_init");self.assertEqual(r["0x005D94C0"]["disposition"],"typed_external");self.assertEqual(d["uncatalogued_gaps"]["functions"],6);self.assertEqual(d["uncatalogued_gaps"]["bytes"],304);self.assertTrue(all(not x["claimed_exact"] for x in d["uncatalogued_gaps"]["records"]))
 def test_provider_fail_closed(self):
  calls=[]
  @PROVIDER
  def provider(_c,m,f,i):calls.append((m.decode(),f.decode()));i.contents.words[0]=13;return 0
  inv=Invocation();self.assertEqual(self.invoke(0x005D91BC,provider,None,ctypes.byref(inv)),0);self.assertEqual(calls,[("pshrec.c","ps_hints_t1stem3")]);self.assertEqual(self.invoke(0x005D9254,provider,None,ctypes.byref(inv)),2);self.assertEqual(self.invoke(0x005D91BC,PROVIDER(),None,ctypes.byref(inv)),3);self.assertEqual(self.invoke(0x005D91BC,provider,None,None),1)
 def test_cli_deterministic(self):
  c=[sys.executable,str(ANALYZER)];a=subprocess.run(c,check=True,capture_output=True,text=True).stdout;b=subprocess.run(c,check=True,capture_output=True,text=True).stdout;self.assertEqual(a,b);self.assertEqual(json.loads(a)["status"],"candidate-qualified-none-batch4")
if __name__=="__main__":unittest.main()
