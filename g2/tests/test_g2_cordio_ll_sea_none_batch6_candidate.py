#!/usr/bin/env python3
from __future__ import annotations
import ctypes,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch6_candidate.py";SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch6/runtime_cordio_ll_sea_none_batch6_candidate.c"
def load_analyzer():
 s=importlib.util.spec_from_file_location("none_batch6",ANALYZER)
 if s is None or s.loader is None:raise RuntimeError("load failed")
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Evidence(ctypes.Structure):_fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure):_fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))
class NoneBatch6Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
  if cc is None:raise unittest.SkipTest("no compiler")
  cls.temp=tempfile.TemporaryDirectory(prefix="none6-");lib=Path(cls.temp.name)/"libnone6.so";subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch6_evidence_count.restype=ctypes.c_size_t;cls.lib.open_cfw_cordio_ll_sea_none_batch6_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch6_evidence.restype=ctypes.POINTER(Evidence);cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch6_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_chained_partition(self):
  d=self.analyzer.run_audit();self.assertEqual(d["status"],"candidate-qualified-none-batch6");self.assertEqual(d["none_group"]["batch6_source_recovered"],{"functions":8,"bytes":2386});self.assertEqual(d["none_group"]["upstream_freetype_source"],{"functions":92,"bytes":13240});self.assertEqual(d["none_group"]["typed_external"],{"functions":106,"bytes":20404});self.assertEqual(d["unsupported_remainder"]["before"],{"functions":114,"bytes":22790});self.assertFalse(d["adapter"]["production_routed"])
 def test_table(self):
  self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch6_evidence_count(),8);total=0;names=[]
  for i in range(8):
   x=self.lib.open_cfw_cordio_ll_sea_none_batch6_evidence(i).contents;total+=x.size;names.append(x.function.decode());self.assertEqual(x.end-x.start,x.size);self.assertEqual(x.module,b"sfdriver.c");self.assertIn(b"FreeType Project License",x.license)
  self.assertEqual(tuple(names),self.analyzer.EXPECTED);self.assertEqual(total,2386);self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch6_evidence(8))
 def test_exact_and_cluster_guards(self):
  d=self.analyzer.run_audit();r=d["none_group"]["records"];self.assertEqual(r["0x005DA1E8"]["upstream_function"],"fmix32");self.assertEqual(r["0x005DA202"]["upstream_function"],"murmur_hash_3_128");self.assertEqual(r["0x005DA73A"]["upstream_function"],"sfnt_get_var_ps_name");self.assertEqual(r["0x005DAB8E"]["disposition"],"typed_external");self.assertEqual(d["uncatalogued_clusters"]["bytes"],148);self.assertTrue(all(not x["claimed_exact"] for x in d["uncatalogued_clusters"]["records"]))
 def test_provider_fail_closed(self):
  calls=[]
  @PROVIDER
  def provider(_c,m,f,i):calls.append((m.decode(),f.decode()));i.contents.words[0]=19;return 0
  inv=Invocation();self.assertEqual(self.invoke(0x005DA656,provider,None,ctypes.byref(inv)),0);self.assertEqual(calls,[("sfdriver.c","fixed2float")]);self.assertEqual(self.invoke(0x005DAB3A,provider,None,ctypes.byref(inv)),2);self.assertEqual(self.invoke(0x005DA656,PROVIDER(),None,ctypes.byref(inv)),3);self.assertEqual(self.invoke(0x005DA656,provider,None,None),1)
 def test_cli_deterministic(self):
  c=[sys.executable,str(ANALYZER)];a=subprocess.run(c,check=True,capture_output=True,text=True).stdout;b=subprocess.run(c,check=True,capture_output=True,text=True).stdout;self.assertEqual(a,b);self.assertEqual(json.loads(a)["status"],"candidate-qualified-none-batch6")
if __name__=="__main__":unittest.main()
