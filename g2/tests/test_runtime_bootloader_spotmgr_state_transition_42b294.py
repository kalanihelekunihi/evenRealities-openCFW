import ctypes,hashlib,importlib.util,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_spotmgr_state_transition_42b294.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42B294;Z=0x42B69C;BASE=0x410000;MAIN_BASE=0x437FE0;MAIN_A=0x5A0FC4;FN="open_cfw_bootloader_spotmgr_state_transition_42b294";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
spec=importlib.util.spec_from_file_location("transition_integrator",ROOT/"tools/integrate_g2_bootloader_spotmgr_state_transition_42b294.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in mod.RS];FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"))
class Model(ctypes.Structure):_fields_=[(x,ctypes.c_uint32)for x in("rank_from","rank_to","secondary_from","secondary_to","current_rank","current_secondary","from_word","to_word","current_word","control80","control44","control4c","control37c","observed","guard_value")]+[(x,ctypes.c_uint8)for x in("active","feature","force_publish","protected_state")]+[(x,ctypes.c_uint32)for x in("pretrim_calls","trim_enable_calls","start_calls","wait_calls","delay_calls","irq_pause_calls","irq_resume_calls","finalize_calls","restore_calls","profile_clear_calls","transition_delay","stored_state")]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"transition.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.step=d.open_cfw_bootloader_spotmgr_state_transition_42b294_portable;cls.step.argtypes=[ctypes.POINTER(Model),ctypes.c_uint32,ctypes.c_uint32];cls.step.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_same_state_guard(self):
  m=Model(observed=4,guard_value=4);self.assertEqual(self.step(ctypes.byref(m),3,3),0);self.assertEqual(m.pretrim_calls,0);m.observed=5;self.assertEqual(self.step(ctypes.byref(m),3,3),0);self.assertEqual(m.pretrim_calls,1)
 def test_forward_start_publish_wake_and_irq(self):
  m=Model(rank_from=9,rank_to=2,secondary_from=8,secondary_to=3,from_word=(19<<21)|(6<<17)|(500<<7)|21,current_word=(11<<21)|7,observed=1,guard_value=1,feature=1,force_publish=1,protected_state=1);self.assertEqual(self.step(ctypes.byref(m),8,1),0);self.assertEqual((m.pretrim_calls,m.trim_enable_calls,m.start_calls,m.wait_calls,m.stored_state),(1,1,1,0,1));self.assertEqual((m.transition_delay,m.delay_calls,m.control37c&0x10000,m.irq_pause_calls,m.irq_resume_calls),(2000,1,0x10000,1,1));self.assertEqual(((m.control80>>10)&15,m.control44&127,m.control4c&127),(6,19,21))
 def test_forward_wait_interpolates(self):
  m=Model(rank_from=8,rank_to=1,secondary_from=7,secondary_to=2,from_word=(3<<21)|(4<<17)|(100<<7)|5,current_word=(4<<21)|6,active=1,force_publish=0);self.assertEqual(self.step(ctypes.byref(m),2,3),0);self.assertEqual((m.trim_enable_calls,m.start_calls,m.wait_calls,m.transition_delay,m.delay_calls),(0,0,1,50,1));self.assertEqual((m.control44&127,m.control4c&127),(4,6))
 def test_reverse_restore_and_finalize(self):
  m=Model(rank_from=2,rank_to=9,secondary_from=3,secondary_to=8,current_rank=5,current_secondary=6,from_word=(9<<21)|(7<<17)|(222<<7)|17,active=1,observed=4,guard_value=3);self.assertEqual(self.step(ctypes.byref(m),4,6),0);self.assertEqual((m.pretrim_calls,m.finalize_calls,m.restore_calls,m.profile_clear_calls),(1,1,1,1));self.assertEqual(((m.control80>>10)&15,m.control44&127,m.control4c&127),(7,9,17))
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),mod.BH);analogue=MAIN.read_bytes()[MAIN_A-MAIN_BASE:MAIN_A-MAIN_BASE+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),996)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual((r["relocation_count"],r["unrelocated_sha256"]),(12,mod.UH))
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
