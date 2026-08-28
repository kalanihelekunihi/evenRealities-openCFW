from __future__ import annotations
import ctypes, hashlib, json, os, struct, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/apollo_main/core_overlay/runtime_cmsis_timer_is_running.c"
FIXTURE=ROOT/"tests/fixtures/runtime_cmsis_timer_is_running_host.c"
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"

class RuntimeCmsisTimerIsRunningTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(); t=Path(cls.temp.name); clang=os.environ.get("OPENCFW_CLANG","/usr/bin/clang")
  lib=t/("timer.dylib" if sys.platform=="darwin" else "timer.so"); cmd=[clang,"-O2","-Wall","-Wextra","-Werror",str(FIXTURE),"-dynamiclib" if sys.platform=="darwin" else "-shared"]
  if sys.platform!="darwin": cmd.append("-fPIC")
  subprocess.run([*cmd,"-o",str(lib)],check=True,capture_output=True,text=True); loaded=ctypes.CDLL(str(lib))
  cls.call=loaded.open_cfw_cmsis_timer_is_running;cls.call.argtypes=[ctypes.c_void_p];cls.call.restype=ctypes.c_uint32
  cls.reset=loaded.open_cfw_test_timer_running_reset;cls.reset.argtypes=[ctypes.c_uint32,ctypes.c_uint32]
  cls.calls=loaded.open_cfw_test_timer_running_calls;cls.calls.restype=ctypes.c_uint32
  obj=t/"leaf.o";flags=["--target=thumbv7em-none-eabi","-mthumb","-O2","-ffreestanding","-fno-jump-tables","-fomit-frame-pointer","-fno-builtin","-mno-unaligned-access","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fropi","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror"]
  subprocess.run([clang,*flags,"-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True,text=True);sys.path.insert(0,str(ROOT/"tools"));import apollo_overlay
  d,s=apollo_overlay.parse_elf32(obj);sec=apollo_overlay.section_named(s,".text.open_cfw_cmsis_timer_is_running");cls.body=d[int(sec["offset"]):int(sec["offset"])+int(sec["size"])];cls.reloc=[]
  for rs in s:
   if int(rs["type"])!=9 or int(rs["info"])!=int(sec["index"]):continue
   st=s[int(rs["link"])];ss=s[int(st["link"])];strings=d[int(ss["offset"]):int(ss["offset"])+int(ss["size"])];names=[]
   for i in range(int(st["size"])//16):f=struct.unpack_from("<IIIBBH",d,int(st["offset"])+i*16);names.append(apollo_overlay.elf_string(strings,f[0],"symbol"))
   for i in range(int(rs["size"])//8):off,info=struct.unpack_from("<II",d,int(rs["offset"])+i*8);cls.reloc.append((off,info&255,names[info>>8]))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_pins(self):
  self.assertEqual((SOURCE.stat().st_size,hashlib.sha256(SOURCE.read_bytes()).hexdigest()),(813,"9e9b8ca7a42f214b381935cf2c32729f7292e3857d166d34f1f6194e40b8845b"));self.assertEqual((FIXTURE.stat().st_size,hashlib.sha256(FIXTURE.read_bytes()).hexdigest()),(537,"f66d76e7a588706e9daa30ff18c9727f26208159a592146db2d5a8f2d6e47a6c"))
  image=OFFICIAL.read_bytes()[32:];stock=image[0x449522-0x438000:0x44953e-0x438000];self.assertEqual((len(stock),hashlib.sha256(stock).hexdigest()),(28,"3802dd7a15e7c36c1e9490f9f538aef562959fae8e695917bc665a9ef435c482"));self.assertEqual((len(self.body),hashlib.sha256(self.body).hexdigest()),(26,"9d9b4fb06604b9c023267b986cafc31ff3d7260fd1cd80f6ba78020d4fcd020b"));self.assertEqual(self.reloc,[(4,10,"open_cfw_cmsis_irq_context"),(18,30,"open_cfw_rtos_timer_is_active")])
 def test_behavior(self):
  for irq,timer,active,result,calls in [(1,0x1234,1,0,0),(0,0,1,0,0),(0,0x1234,0,0,1),(0,0x1234,1,1,1)]:
   self.reset(irq,active);self.assertEqual(self.call(ctypes.c_void_p(timer)),result);self.assertEqual(self.calls(),calls)
 def test_production_registration_is_atomic(self):
  config=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text());manifest=json.loads((ROOT/"manifests/g2-2.2.6.10-core-source.json").read_text())
  leaf=next(item for item in config["relocated_leaves"] if item["function"]=="open_cfw_cmsis_timer_is_running")
  self.assertEqual(leaf["expected"]["sha256"],"8581df567ff213627c862263b15df54e96a97212642518b62f13e3904775a0a3");self.assertEqual(leaf["toolchain_profiles"]["linux-clang"]["expected"]["sha256"],"edf51330c2dd4d59992f0e427a8e4234bca96fcbcf02437097990b3838b406ee")
  self.assertEqual(sum(site["target_function"]==leaf["function"] for site in config["patch_sites"]),1);regions=manifest["component_overrides"]["apollo_main"]["regions"]
  self.assertEqual(sum(region["name"]=="apollo_cmsis_timer_is_running_source_leaf" for region in regions),1)

if __name__=="__main__":unittest.main()
