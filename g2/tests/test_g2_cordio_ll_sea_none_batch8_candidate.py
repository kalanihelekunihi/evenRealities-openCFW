#!/usr/bin/env python3
from __future__ import annotations
import ctypes,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch8_candidate.py";SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch8/runtime_cordio_ll_sea_none_batch8_candidate.c"
def load_analyzer():
 s=importlib.util.spec_from_file_location("none_batch8",ANALYZER)
 if s is None or s.loader is None:raise RuntimeError("load failed")
 m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Evidence(ctypes.Structure):_fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure):_fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))
class NoneBatch8Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
  if cc is None:raise unittest.SkipTest("no compiler")
  cls.temp=tempfile.TemporaryDirectory(prefix="none8-");lib=Path(cls.temp.name)/"libnone8.so";subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
  cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch8_evidence_count.restype=ctypes.c_size_t;cls.lib.open_cfw_cordio_ll_sea_none_batch8_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch8_evidence.restype=ctypes.POINTER(Evidence);cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch8_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_chained_partition(self):
  d=self.analyzer.run_audit();self.assertEqual(d["status"],"candidate-qualified-none-batch8");self.assertEqual(d["none_group"]["batch8_source_recovered"],{"functions":6,"bytes":2602});self.assertEqual(d["none_group"]["upstream_freetype_source"],{"functions":105,"bytes":19176});self.assertEqual(d["none_group"]["typed_external"],{"functions":93,"bytes":14468});self.assertEqual(d["unsupported_remainder"]["before"],{"functions":99,"bytes":17070});self.assertFalse(d["adapter"]["production_routed"])
 def test_table(self):
  self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch8_evidence_count(),6);total=0;names=[]
  for i in range(6):
   x=self.lib.open_cfw_cordio_ll_sea_none_batch8_evidence(i).contents;total+=x.size;names.append(x.function.decode());self.assertEqual(x.end-x.start,x.size);self.assertEqual(x.module,b"ttcmap.c");self.assertIn(b"FreeType Project License",x.license)
  self.assertEqual(tuple(names),self.analyzer.EXPECTED);self.assertEqual(total,2602);self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch8_evidence(6))
 def test_exact_and_cluster_guards(self):
  d=self.analyzer.run_audit();r=d["none_group"]["records"];self.assertEqual(r["0x005DC99C"]["upstream_function"],"tt_cmap4_set_range");self.assertEqual(r["0x005DCB16"]["upstream_function"],"tt_cmap4_validate");self.assertEqual(r["0x005DCFF6"]["upstream_function"],"tt_cmap4_char_map_binary");self.assertEqual(r["0x005DD584"]["disposition"],"typed_external");self.assertEqual(d["uncatalogued_clusters"]["bytes"],888);self.assertTrue(all(not x["claimed_exact"] for x in d["uncatalogued_clusters"]["records"]))
 def test_provider_fail_closed(self):
  calls=[]
  @PROVIDER
  def provider(_c,m,f,i):calls.append((m.decode(),f.decode()));i.contents.words[0]=29;return 0
  inv=Invocation();self.assertEqual(self.invoke(0x005DCB16,provider,None,ctypes.byref(inv)),0);self.assertEqual(calls,[("ttcmap.c","tt_cmap4_validate")]);self.assertEqual(self.invoke(0x005DD3C6,provider,None,ctypes.byref(inv)),2);self.assertEqual(self.invoke(0x005DCB16,PROVIDER(),None,ctypes.byref(inv)),3);self.assertEqual(self.invoke(0x005DCB16,provider,None,None),1)
 def test_cli_deterministic(self):
  c=[sys.executable,str(ANALYZER)];a=subprocess.run(c,check=True,capture_output=True,text=True).stdout;b=subprocess.run(c,check=True,capture_output=True,text=True).stdout;self.assertEqual(a,b);self.assertEqual(json.loads(a)["status"],"candidate-qualified-none-batch8")
if __name__=="__main__":unittest.main()
