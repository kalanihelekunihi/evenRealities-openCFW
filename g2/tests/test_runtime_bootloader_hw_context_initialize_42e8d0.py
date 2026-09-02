import ctypes,hashlib,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_hw_context_initialize_42e8d0.c";BOOT=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";MAIN=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";A=0x42E8D0;Z=0x42EA32;BASE=0x410000;MB=0x437FE0;MA=0x55D94C;FN="open_cfw_bootloader_hw_context_initialize_42e8d0";sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay  # noqa:E402
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-mllvm","-enable-machine-outliner=never");PROFILES=(ROOT/".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",Path("/opt/homebrew/opt/llvm@22/bin/clang"));SPECS=((0x94,"open_cfw_bootloader_config_read_421548",0x421548),(0xA4,"open_cfw_bootloader_config_read_421548",0x421548),(0xB6,"open_cfw_bootloader_config_read_421548",0x421548),(0x116,"open_cfw_bootloader_config_read_421548",0x421548),(0x126,"open_cfw_bootloader_config_read_421548",0x421548));RELOCS=[{"offset":o,"type":"R_ARM_THM_CALL","symbol":n,"symbol_type":"STT_NOTYPE","target_address":t}for o,n,t in SPECS]
class Model(ctypes.Structure):_fields_=[("slot_word",ctypes.c_uint32),("slot_index",ctypes.c_uint32),("retained_magic",ctypes.c_uint32),("retained_primary",ctypes.c_uint32*3),("retained_secondary",ctypes.c_uint32*2),("read_status",ctypes.c_uint32*5),("read_primary",ctypes.c_uint32*3),("read_secondary",ctypes.c_uint32*2),("primary",ctypes.c_uint32*3),("secondary",ctypes.c_uint32*2),("control_register",ctypes.c_uint32),("slot_pointer",ctypes.c_uint32),("primary_valid",ctypes.c_uint8),("secondary_valid",ctypes.c_uint8)]
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/"init.so";cc=shutil.which("cc")or shutil.which("clang");subprocess.run([cc,"-std=c11","-O2","-fPIC","-shared",str(SOURCE),"-o",str(lib)],check=True,capture_output=True,text=True);d=ctypes.CDLL(str(lib));cls.init=d.open_cfw_bootloader_hw_context_initialize_42e8d0_portable;cls.init.argtypes=[ctypes.c_uint32,ctypes.c_uint32,ctypes.POINTER(Model)];cls.init.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_guards_and_claim(self):
  m=Model();self.assertEqual(self.init(1,1,ctypes.byref(m)),5);self.assertEqual(self.init(0,0,ctypes.byref(m)),6);m.slot_word=1<<24;self.assertEqual(self.init(0,1,ctypes.byref(m)),7)
 def test_read_profiles_and_validity(self):
  m=Model(control_register=3);m.read_primary[:]=(1,2,3);m.read_secondary[:]=(4,5);self.assertEqual(self.init(0,1,ctypes.byref(m)),0);self.assertEqual(m.slot_word,0x01AFAFAF);self.assertEqual(list(m.primary),[1,2,3]);self.assertEqual(list(m.secondary),[5,4]);self.assertEqual((m.primary_valid,m.secondary_valid,m.control_register&1),(1,1,0))
 def test_defaults_and_retained_profiles(self):
  m=Model();m.read_status[0]=1;self.assertEqual(self.init(0,1,ctypes.byref(m)),0);self.assertEqual(list(m.primary),[0x4395C000,0x3F839874,0xBB8C47A1]);self.assertEqual(m.primary_valid,0)
  m=Model(retained_magic=0x1F01600D);m.retained_primary[:]=(7,8,9);m.retained_secondary[:]=(10,11);self.assertEqual(self.init(0,1,ctypes.byref(m)),0);self.assertEqual(list(m.primary),[7,8,9]);self.assertEqual(list(m.secondary),[11,10])
 def test_dual_toolchain_exact_and_main_analogue(self):
  stock=BOOT.read_bytes()[A-BASE:Z-BASE];self.assertEqual(hashlib.sha256(stock).hexdigest(),"21eb4fbe548c1f7c1c16bbf7bf31671f7cdbf125ee784a96893efdef723f6fd8");analogue=MAIN.read_bytes()[MA-MB:MA-MB+len(stock)];self.assertEqual(sum(a==b for a,b in zip(stock,analogue)),339)
  with tempfile.TemporaryDirectory()as t:
   for i,cc in enumerate(PROFILES):
    o=Path(t)/f"{i}.o";subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(o)],check=True,capture_output=True,text=True);body,r=apollo_overlay.extract_in_place_function_section(o,FN,runtime_address=A,relocation_configs=RELOCS,strict_relocation_contract=True,allow_discarded_alloc_sections=True);self.assertEqual(body,stock);self.assertEqual(r["relocation_count"],5);self.assertEqual(r["unrelocated_sha256"],"b34fa81a3f580579a5260a539ef14f81e8b7bfdbbed0978e88dbba4c69e17c06")
 def test_reviewable(self):
  for token in(".byte",".short",".word",".inst"):self.assertNotIn(token,SOURCE.read_text())
if __name__=="__main__":unittest.main()
