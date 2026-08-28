#!/usr/bin/env python3
from __future__ import annotations
import ctypes, importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ANALYZER=ROOT/"tools/analyze_em9305_master_connection_boundary.py"; SOURCE=ROOT/"components/shared/em9305/runtime_controller_master_connection_boundary.c"
def load():
 sys.path.insert(0,str(ROOT/"tools"));s=importlib.util.spec_from_file_location("analyze_em9305_master_connection_boundary",ANALYZER);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class Invocation(ctypes.Structure):_fields_=[("words",ctypes.c_size_t*8)]
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(Invocation))
class Ports(ctypes.Structure):_fields_=[("context",ctypes.c_void_p),("provider",PROVIDER)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=load();cc=shutil.which("clang") or shutil.which("cc");cls.cc=cc;cls.t=tempfile.TemporaryDirectory();lib=Path(cls.t.name)/"x.so";subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),str(SOURCE),"-o",str(lib)],check=True);cls.f=ctypes.CDLL(str(lib)).open_cfw_em9305_mst_conn_boundary;cls.f.argtypes=[ctypes.POINTER(Ports),ctypes.c_int,ctypes.POINTER(Invocation)];cls.f.restype=ctypes.c_int32
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def test_audit(self):
  r=self.a.run_audit();self.assertEqual((r["decision"]["bytes"],r["entry_count"]),(1564,3));self.assertFalse(r["exact_source_available"]);self.assertFalse(r["candidate"]["production_routed"]);self.assertEqual(r["hardware_validation"],"deferred by project direction")
 def test_fail_closed_and_forward(self):
  i=Invocation();p=Ports();self.assertEqual(self.f(None,0,ctypes.byref(i)),1);self.assertEqual(self.f(ctypes.byref(p),0,ctypes.byref(i)),2);calls=[]
  @PROVIDER
  def cb(_c,e,_i):calls.append(e);return 0
  p=Ports(None,cb)
  for e in range(3):self.assertEqual(self.f(ctypes.byref(p),e,ctypes.byref(i)),0)
  self.assertEqual(calls,[0,1,2]);self.assertEqual(self.f(ctypes.byref(p),3,ctypes.byref(i)),1)
 def test_provider_failure(self):
  @PROVIDER
  def cb(_c,_e,_i):return 1
  self.assertEqual(self.f(ctypes.byref(Ports(None,cb)),1,ctypes.byref(Invocation())),3)
 def test_no_undefined_imports(self):
  o=Path(self.t.name)/"x.o";subprocess.run([self.cc,"-std=c11","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-I",str(SOURCE.parent),"-c",str(SOURCE),"-o",str(o)],check=True);self.assertEqual(subprocess.run(["nm","-u",str(o)],capture_output=True,text=True,check=True).stdout.strip(),"")
 def test_json(self):
  e=os.environ.copy();e["PYTHONDONTWRITEBYTECODE"]="1";r=subprocess.run([sys.executable,str(ANALYZER),"--json"],cwd=ROOT,env=e,capture_output=True,text=True,check=True);self.assertEqual(json.loads(r.stdout)["entry_count"],3)
if __name__=="__main__":unittest.main()
