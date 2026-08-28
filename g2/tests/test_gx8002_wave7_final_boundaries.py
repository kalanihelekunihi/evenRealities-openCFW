#!/usr/bin/env python3
from __future__ import annotations
import ctypes,importlib.util,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TOOLS=ROOT/"tools";A=TOOLS/"analyze_gx8002_source_readiness.py";D=ROOT/"components/shared/gx8002";COMMON=D/"runtime_gx8002_kws_model_boundary.c";BLOB=ROOT/"blobs/official/g2-2.2.6.10/firmware_codec.bin"
SOURCES=(D/"runtime_gx8002_kws_command_boundary.c",D/"runtime_gx8002_image_a_sram_data_boundary.c",D/"runtime_gx8002_image_b_sram_data_boundary.c")
SEGMENTS={"open_cfw_gx8002_kws_command_load":(0x18D90,9164),"open_cfw_gx8002_image_a_sram_data_load":(0x184FC,2196),"open_cfw_gx8002_image_b_sram_data_load":(0x4EE5C,2928)}
PROVIDER=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t))
class Ports(ctypes.Structure):_fields_=[("context",ctypes.c_void_p),("provider",PROVIDER)]
def load():
 sys.path.insert(0,str(TOOLS));s=importlib.util.spec_from_file_location("gx8002_wave7",A);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
class GX8002Wave7Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=load().run_audit();cls.cc=shutil.which("clang") or shutil.which("cc");cls.t=tempfile.TemporaryDirectory();lib=Path(cls.t.name)/"x.so";subprocess.run([cls.cc,"-std=c11","-O2","-ffreestanding","-fno-builtin","-fno-stack-protector","-Wall","-Wextra","-Werror","-I",str(D),"-fPIC","-shared",str(COMMON),*map(str,SOURCES),"-o",str(lib)],check=True,capture_output=True,text=True);loaded=ctypes.CDLL(str(lib));cls.f={};cls.blob=BLOB.read_bytes()
  for name in SEGMENTS:fn=getattr(loaded,name);fn.argtypes=[ctypes.POINTER(Ports),ctypes.POINTER(ctypes.c_uint8),ctypes.c_size_t];fn.restype=ctypes.c_int32;cls.f[name]=fn
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def test_final_evidence_and_zero_unclassified_residual(self):
  c=self.r["latest_cluster"];self.assertEqual((c["name"],c["start"],c["end_exclusive"],c["size"]),("image_a_kws_command",0x18D90,0x1B15C,9164));self.assertIn("no reconstruction claimed",c["semantics"]);self.assertEqual(c["dram_staging"],"0x20003304 (decoded)")
  extras={x["name"]:x for x in self.r["additional_clusters"]};self.assertEqual((extras["image_b_sram_data"]["size"],extras["image_a_sram_data"]["size"]),(2928,2196));self.assertIn("derived",extras["image_b_sram_data"]["boundary_confidence"])
  for x in (c,*extras.values()):self.assertEqual(x["boundary_license"],"MIT");self.assertEqual(x["payload_source_license"],"NOASSERTION");self.assertEqual(x["payload_redistribution_authority"],"unresolved");self.assertFalse(x["production_routed"])
  self.assertEqual(self.r["readiness"]["unavailable_proprietary_codec_firmware"],{"spans":0,"bytes":0});self.assertEqual(self.r["latest_wave_delta"],{"typed_external":{"spans":3,"bytes":14288},"proprietary_unavailable":{"spans":-3,"bytes":-14288},"source_owned_bytes":0,"blocking_bytes":0})
 def test_exact_and_mutated_segments(self):
  for name,(start,size) in SEGMENTS.items():
   body=self.blob[start:start+size];out=(ctypes.c_uint8*size)()
   def make(mutate):
    @PROVIDER
    def cb(_c,d,_n,w):ctypes.memmove(d,body,size);d[size//2]^=1 if mutate else 0;w[0]=size;return 0
    return cb
   ok=make(False);self.assertEqual(self.f[name](ctypes.byref(Ports(None,ok)),out,size),0);self.assertEqual(bytes(out),body);bad=make(True);self.assertEqual(self.f[name](ctypes.byref(Ports(None,bad)),out,size),4);self.assertEqual(bytes(out),b"\0"*size)
 def test_missing_short_and_failed_provider(self):
  name="open_cfw_gx8002_kws_command_load";size=9164;out=(ctypes.c_uint8*size)(*([0xA5]*size));self.assertEqual(self.f[name](ctypes.byref(Ports(None,PROVIDER())),out,size),2)
  @PROVIDER
  def short(_c,d,_n,w):d[0]=1;w[0]=1;return 0
  self.assertEqual(self.f[name](ctypes.byref(Ports(None,short)),out,size),4);self.assertEqual(bytes(out),b"\0"*size)
  @PROVIDER
  def failed(_c,d,_n,w):d[0]=1;w[0]=1;return -1
  self.assertEqual(self.f[name](ctypes.byref(Ports(None,failed)),out,size),3);self.assertEqual(bytes(out),b"\0"*size)
 def test_host_and_m55_import_graph(self):
  for target,tf in (("host",[]),("m55",["--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb"])):
   objs=[]
   for src in (COMMON,*SOURCES):
    o=Path(self.t.name)/f"{target}-{src.stem}.o";subprocess.run([self.cc,*tf,"-std=c11","-Oz","-ffreestanding","-fno-builtin","-fno-stack-protector","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-I",str(D),"-c",str(src),"-o",str(o)],check=True,capture_output=True,text=True);objs.append(o)
   text=subprocess.run(["nm","-u",*map(str,objs)],check=True,capture_output=True,text=True).stdout;symbols=[line.rsplit(maxsplit=1)[-1].lstrip("_") for line in text.splitlines() if line.strip() and not line.rstrip().endswith(":")];self.assertEqual(symbols,["open_cfw_gx8002_authenticated_segment_load"]*3)
if __name__=="__main__":unittest.main()
