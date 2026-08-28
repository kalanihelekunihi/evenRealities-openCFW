#!/usr/bin/env python3
from __future__ import annotations
import ctypes, importlib.util, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ANALYZER=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch2_candidate.py"
SOURCE=ROOT/"research/candidates/cordio_ll_sea_none_batch2/runtime_cordio_ll_sea_none_batch2_candidate.c"

def load_analyzer():
    spec=importlib.util.spec_from_file_location("none_batch2",ANALYZER)
    if spec is None or spec.loader is None: raise RuntimeError("load failed")
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module
class Evidence(ctypes.Structure):
    _fields_=[("start",ctypes.c_uint32),("end",ctypes.c_uint32),("size",ctypes.c_size_t),("module",ctypes.c_char_p),("function",ctypes.c_char_p),("license",ctypes.c_char_p)]
class Invocation(ctypes.Structure): _fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.POINTER(Invocation))

class NoneBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer=load_analyzer();cc=shutil.which("clang") or shutil.which("cc")
        if cc is None: raise unittest.SkipTest("no compiler")
        cls.temp=tempfile.TemporaryDirectory(prefix="none2-");lib=Path(cls.temp.name)/"libnone2.so"
        subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True)
        cls.lib=ctypes.CDLL(str(lib));cls.lib.open_cfw_cordio_ll_sea_none_batch2_evidence_count.restype=ctypes.c_size_t
        cls.lib.open_cfw_cordio_ll_sea_none_batch2_evidence.argtypes=[ctypes.c_size_t];cls.lib.open_cfw_cordio_ll_sea_none_batch2_evidence.restype=ctypes.POINTER(Evidence)
        cls.invoke=cls.lib.open_cfw_cordio_ll_sea_none_batch2_candidate;cls.invoke.argtypes=[ctypes.c_uint32,PROVIDER,ctypes.c_void_p,ctypes.POINTER(Invocation)];cls.invoke.restype=ctypes.c_int
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_chained_audit_partition(self):
        data=self.analyzer.run_audit();self.assertEqual(data["status"],"candidate-qualified-none-batch2")
        self.assertEqual(data["none_group"]["batch2_source_recovered"],{"functions":18,"bytes":2750})
        self.assertEqual(data["none_group"]["upstream_freetype_source"],{"functions":28,"bytes":4114})
        self.assertEqual(data["none_group"]["typed_external"],{"functions":170,"bytes":29530})
        self.assertEqual(data["unsupported_remainder"]["before"],{"functions":188,"bytes":32280})
        self.assertFalse(data["adapter"]["production_routed"]);self.assertFalse(data["hardware_operations"])
    def test_exact_table_and_source_order(self):
        self.assertEqual(self.lib.open_cfw_cordio_ll_sea_none_batch2_evidence_count(),18);names=[];total=0;last=0
        for index in range(18):
            item=self.lib.open_cfw_cordio_ll_sea_none_batch2_evidence(index).contents;total+=item.size;names.append(item.function.decode())
            self.assertEqual(item.end-item.start,item.size);self.assertGreater(item.start,last);last=item.start
            self.assertEqual(item.module,b"pshalgo.c");self.assertIn(b"FreeType Project License",item.license)
        self.assertEqual(tuple(names),self.analyzer.EXPECTED);self.assertEqual(total,2750)
        self.assertFalse(self.lib.open_cfw_cordio_ll_sea_none_batch2_evidence(18))
    def test_representative_exact_and_residual_guard(self):
        records=self.analyzer.run_audit()["none_group"]["records"]
        self.assertEqual(records["0x005D7340"]["upstream_function"],"psh_dimension_quantize_len")
        self.assertEqual(records["0x005D761A"]["upstream_function"],"psh_glyph_compute_inflections")
        self.assertEqual(records["0x005D784A"]["upstream_function"],"psh_glyph_init")
        self.assertEqual(records["0x005D7B62"]["disposition"],"typed_external")
    def test_provider_boundary_fail_closed(self):
        calls=[]
        @PROVIDER
        def provider(_context,module,function,invocation):
            calls.append((module.decode(),function.decode()));invocation.contents.words[0]=9;return 0
        invocation=Invocation()
        self.assertEqual(self.invoke(0x005D7782,provider,None,ctypes.byref(invocation)),0)
        self.assertEqual(calls,[("pshalgo.c","psh_compute_dir")]);self.assertEqual(invocation.words[0],9)
        self.assertEqual(self.invoke(0x005D7B62,provider,None,ctypes.byref(invocation)),2)
        self.assertEqual(self.invoke(0x005D7782,PROVIDER(),None,ctypes.byref(invocation)),3)
        self.assertEqual(self.invoke(0x005D7782,provider,None,None),1)
    def test_cli_deterministic(self):
        command=[sys.executable,str(ANALYZER)];first=subprocess.run(command,check=True,capture_output=True,text=True).stdout;second=subprocess.run(command,check=True,capture_output=True,text=True).stdout
        self.assertEqual(first,second);self.assertEqual(json.loads(first)["status"],"candidate-qualified-none-batch2")
if __name__=="__main__":unittest.main()
