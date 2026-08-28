from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mspi_sector_erase_420a08.c"
FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mspi_sector_erase_host.c"

class MspiSectorEraseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory(); suffix="x.dylib" if sys.platform=="darwin" else "x.so"; cls.p=Path(cls.t.name)/suffix
  subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(cls.p)],check=True,capture_output=True)
  cls.lib=ctypes.CDLL(str(cls.p));cls.lib.open_cfw_sector_erase_fixture_config.argtypes=[ctypes.c_uint32,ctypes.c_uint32];cls.lib.open_cfw_sector_erase_fixture_value.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_sector_erase_fixture_value.restype=ctypes.c_uint32;cls.lib.open_cfw_bootloader_mspi_sector_erase_420a08.argtypes=[ctypes.c_uint32];cls.lib.open_cfw_bootloader_mspi_sector_erase_420a08.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.t.cleanup()
 def setUp(self):self.lib.open_cfw_sector_erase_fixture_reset()
 def cfg(self,f,v):self.lib.open_cfw_sector_erase_fixture_config(f,v)
 def v(self,f):return self.lib.open_cfw_sector_erase_fixture_value(f)
 def events(self):return tuple(self.v(i) for i in range(self.v(16)))
 def test_authenticated_stock_body_pool_and_caller(self):
  b=OFFICIAL.read_bytes();body=b[0x10A08:0x10ADA];self.assertEqual((len(body),hashlib.sha256(body).hexdigest()),(210,"0a0a96db9e3a1c6fcbdfcebd96db6f16e22c780940889677a16ebc880d0dd899"));pool=b[0x109FC:0x10A08];self.assertEqual((len(pool),hashlib.sha256(pool).hexdigest()),(12,"24e3dd42d22fb00fcda8010047ae549a2110c8e5c77f230fb43a071466a26aa4"));self.assertEqual(b[0x11354:0x11358].hex(),"fff758fb")
 def test_validation_short_circuits(self):
  self.cfg(0,0);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0),2);self.assertEqual(self.events(),())
  self.setUp();self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(1),6);self.assertEqual(self.v(21),1);self.assertEqual(self.events(),())
  self.setUp();self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x02000000),5);self.assertEqual(self.events(),())
 def test_wait_and_command_failure_cleanup(self):
  self.cfg(1,1);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),3);self.assertEqual(self.events(),(1,2,3,4));self.assertEqual((self.v(18),self.v(19),self.v(20)),(0x432148,0x123000,0))
  self.setUp();self.cfg(2,7);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),7);self.assertEqual(self.events(),(1,2,5,3,4));self.assertEqual((self.v(18),self.v(20)),(0x43267c,7))
  self.setUp();self.cfg(3,8);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),8);self.assertEqual(self.events(),(1,2,5,6,3,4));self.assertEqual((self.v(18),self.v(20)),(0x432178,8))
 def test_postwait_disable_and_success(self):
  self.cfg(4,1);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),4);self.assertEqual(self.events(),(1,2,5,6,3,4));self.assertEqual(self.v(18),0x4321a8)
  self.setUp();self.cfg(5,9);self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),9);self.assertEqual(self.events(),(1,2,5,6,7,3,4));self.assertEqual((self.v(18),self.v(20)),(0x4321d8,9))
  self.setUp();self.assertEqual(self.lib.open_cfw_bootloader_mspi_sector_erase_420a08(0x123000),0);self.assertEqual(self.events(),(1,2,5,6,7,3,4));self.assertEqual(tuple(self.v(i) for i in range(22,27)),(0x20,0x123000,1,0,0));self.assertEqual(self.v(17),0)
 def test_source_cross_compiles_for_cortex_m55(self):
  out=Path(self.t.name)/"target.o";subprocess.run([os.environ.get("CC","/usr/bin/clang"),"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(out)],check=True,capture_output=True);self.assertTrue(out.is_file())
if __name__=="__main__":unittest.main()
