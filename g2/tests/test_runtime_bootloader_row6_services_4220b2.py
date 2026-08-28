from __future__ import annotations
import ctypes, hashlib, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_row6_services_4220b2.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_row6_services_host.c"

class BootloaderRow6ServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); cls.library = Path(cls.tmp.name) / ("row6.dylib" if sys.platform == "darwin" else "row6.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(cls.library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library)); cls.enable = cls.lib.open_cfw_bootloader_row6_enable_4220b2; cls.enable.argtypes=[ctypes.c_uint32]; cls.enable.restype=ctypes.c_uint32; cls.disable=cls.lib.open_cfw_bootloader_row6_disable_422220; cls.disable.argtypes=[ctypes.c_uint32]; cls.disable.restype=ctypes.c_uint32; cls.dispatch=cls.lib.open_cfw_bootloader_mode_dispatch_4222a0; cls.dispatch.argtypes=[ctypes.c_uint32,ctypes.c_size_t,ctypes.POINTER(ctypes.c_uint32)]; cls.dispatch.restype=ctypes.c_uint32
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def setUp(self): self.lib.open_cfw_row6_fixture_reset()
    def u32(self,n): return ctypes.c_uint32.in_dll(self.lib,n)
    def u8(self,n): return ctypes.c_uint8.in_dll(self.lib,n)
    def array(self,n): return (ctypes.c_uint32*2).in_dll(self.lib,n)

    def test_authenticated_bodies_seams_and_successor(self):
        b=OFFICIAL.read_bytes(); spans=[(0x120B2,0x1220E,"701cc62514c5618aece1f206044e7815375082c6e4a9afa4eafd0e331f331e96"),(0x12220,0x1228E,"f26f053665f5477df6aa97d2e596f08b7045112332919102a5b1dd72d219ea36"),(0x122A0,0x122D2,"7da05bfcd4b489183db4a2a1becfbe3bb7a0e3dc297e74e632c00e454d653164")]
        for a,z,h in spans: self.assertEqual((z-a,hashlib.sha256(b[a:z]).hexdigest()),(z-a,h))
        self.assertEqual(hashlib.sha256(b[0x1220E:0x12220]).hexdigest(),"34fb2e40d40a342dcdc1d23c99581a89280341ef5be58a15a5765d4328a99a9e"); self.assertEqual(hashlib.sha256(b[0x1228E:0x122A0]).hexdigest(),"08388290f49d6fd437c9ccef1aaab3fe54465ec3d251b281f154e02e341a151a"); self.assertEqual(b[0x122D2:0x122D6].hex(),"00005005")

    def test_first_client_creates_configures_starts_and_finalizes(self):
        self.assertEqual(self.enable(0x103),0); self.assertEqual(self.array("open_cfw_row6_fixture_bitmap")[0],1<<3); self.assertEqual(self.u32("open_cfw_row6_host_handle").value,0x1234)
        self.assertEqual((self.u32("open_cfw_row6_fixture_create_calls").value,self.u32("open_cfw_row6_fixture_configure_calls").value,self.u32("open_cfw_row6_fixture_start_calls").value,self.u32("open_cfw_row6_fixture_finalize_calls").value),(1,1,1,1)); self.assertEqual(tuple(self.array("open_cfw_row6_fixture_enable_calls")),(1,1)); self.assertEqual(tuple(self.array("open_cfw_row6_fixture_disable_calls")),(0,1))

    def test_not_ready_and_start_failure_roll_back(self):
        self.u8("open_cfw_row6_host_ready").value=0; self.assertEqual(self.enable(1),1); self.assertEqual(self.array("open_cfw_row6_fixture_bitmap")[0],0)
        self.lib.open_cfw_row6_fixture_reset(); self.u32("open_cfw_row6_fixture_start_status").value=8; self.assertEqual(self.enable(2),8); self.assertEqual(self.array("open_cfw_row6_fixture_bitmap")[0],0); self.assertEqual(self.u32("open_cfw_row6_fixture_destroy_calls").value,1); self.assertEqual(self.u32("open_cfw_row6_host_handle").value,0)

    def test_existing_client_is_idempotent(self):
        self.array("open_cfw_row6_fixture_bitmap")[0]=1<<4; self.assertEqual(self.enable(4),0); self.assertEqual(self.u32("open_cfw_row6_fixture_create_calls").value,0); self.assertEqual(self.u32("open_cfw_row6_fixture_restore_calls").value,0)

    def test_disable_absent_nonfinal_and_final(self):
        self.assertEqual(self.disable(1),0); self.assertEqual(self.u32("open_cfw_row6_fixture_stop_calls").value,0)
        self.array("open_cfw_row6_fixture_bitmap")[0]=(1<<1)|(1<<2); self.disable(1); self.assertEqual(self.u32("open_cfw_row6_fixture_stop_calls").value,0)
        self.u32("open_cfw_row6_host_handle").value=0x777; self.u8("open_cfw_row6_host_pending").value=1; self.disable(2); self.assertEqual((self.u32("open_cfw_row6_fixture_stop_calls").value,self.u32("open_cfw_row6_fixture_destroy_calls").value),(1,1)); self.assertEqual(self.u32("open_cfw_row6_host_handle").value,0); self.assertEqual(self.array("open_cfw_row6_fixture_disable_calls")[0],1)

    def test_dispatch_low_byte_routes_four_through_six(self):
        cfg=ctypes.c_uint32(7)
        for k in (4,5,6): self.assertEqual(self.dispatch(0x100+k,3,ctypes.byref(cfg)),0x40+k); self.assertEqual(self.u32("open_cfw_row6_fixture_dispatch_kind").value,k)
        self.assertEqual(self.dispatch(7,3,ctypes.byref(cfg)),7)

    def test_source_cross_compiles_for_cortex_m55(self):
        for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(cc).exists(): continue
            subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(self.tmp.name)/(Path(cc).parent.name+"-row6.o"))],check=True,capture_output=True)

if __name__ == "__main__": unittest.main()
