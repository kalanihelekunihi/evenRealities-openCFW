#!/usr/bin/env python3
from __future__ import annotations
import ctypes, importlib.util, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch1_candidate.py"
SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch1/runtime_cordio_ll_sea_none_batch1_candidate.c"

def load_analyzer():
    s=importlib.util.spec_from_file_location("none_batch1",ANALYZER)
    if s is None or s.loader is None: raise RuntimeError("load failed")
    m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Evidence(ctypes.Structure):
    _fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure): _fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))

class NoneBatch1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
        if cc is None: raise unittest.SkipTest("no compiler")
        cls.temp=tempfile.TemporaryDirectory(prefix="none1-");lib=Path(cls.temp.name)/"libnone1.so"
        subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
        cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch1_evidence_count.restype=ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch1_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch1_evidence.restype=ctypes.POINTER(Evidence)
        cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch1_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_audit_partition(self):
        d=self.analyzer.run_audit();self.assertEqual(d["status"],"candidate-qualified-none-batch1")
        self.assertEqual(d["none_group"]["upstream_freetype_source"],{"functions":10,"bytes":1364})
        self.assertEqual(d["none_group"]["typed_external"],{"functions":188,"bytes":32280})
        self.assertEqual(d["unsupported_remainder"]["after"],{"functions":188,"bytes":32280})
        self.assertFalse(d["adapter"]["production_routed"])
    def test_table(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch1_evidence_count(),10);total=0
        for i in range(10):
            x=self.lib.open_cfw_cordio_ll_sea_none_batch1_evidence(i).contents;total+=x.size
            self.assertEqual(x.end-x.start,x.size);self.assertIn(b"FreeType Project License",x.license)
        self.assertEqual(total,1364);self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch1_evidence(10))
    def test_exact_representatives_and_external_guard(self):
        r=self.analyzer.run_audit()["none_group"]["records"]
        self.assertEqual(r["0x005D188A"]["upstream_function"],"ps_builder_add_point")
        self.assertEqual(r["0x005D1F26"]["upstream_function"],"t1_decoder_parse_metrics")
        self.assertEqual(r["0x005D2250"]["upstream_function"],"cff_decoder_prepare")
        self.assertEqual(r["0x005D1D2A"]["disposition"],"typed_external")
    def test_provider_boundary(self):
        calls=[]
        @PROVIDER
        def provider(_c,m,f,i): calls.append((m.decode(),f.decode()));i.contents.words[0]=5;return 0
        inv=Invocation();self.assertEqual(self.invoke(0x005D2170,provider,None,ctypes.byref(inv)),0)
        self.assertEqual(calls,[("cffdecode.c","cff_compute_bias")]);self.assertEqual(self.invoke(0x005D1D2A,provider,None,ctypes.byref(inv)),2)
        self.assertEqual(self.invoke(0x005D2170,PROVIDER(),None,ctypes.byref(inv)),3);self.assertEqual(self.invoke(0x005D2170,provider,None,None),1)
    def test_cli_deterministic(self):
        c=[sys.executable,str(ANALYZER)];a=subprocess.run(c,check=True,capture_output=True,text=True).stdout;b=subprocess.run(c,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b);self.assertEqual(json.loads(a)["status"],"candidate-qualified-none-batch1")
if __name__=="__main__":unittest.main()
