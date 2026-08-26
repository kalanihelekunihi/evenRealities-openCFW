import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/apollo_main/core_overlay/cordio_sec_api.c"
FIXTURE=ROOT/"tests/fixtures/cordio_sec_api_host.c"
HEADER=ROOT/"tests/fixtures/cordio_sec_api_host.h"

class CordioSecApiCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.path=Path(cls.temp.name)/"libsec.so"
  subprocess.run(["/usr/bin/clang","-std=c11","-shared","-fPIC","-O2","-Wall","-Wextra","-Werror","-include",str(HEADER),str(SOURCE),str(FIXTURE),"-o",str(cls.path)],check=True)
  cls.lib=ctypes.CDLL(str(cls.path));cls.lib.open_cfw_cordio_sec_random.argtypes=[ctypes.c_void_p,ctypes.c_uint8]
  cls.lib.open_cfw_cordio_sec_aes.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint8,ctypes.c_uint16,ctypes.c_uint8];cls.lib.open_cfw_cordio_sec_aes.restype=ctypes.c_uint8
  cls.lib.open_cfw_cordio_sec_cmac_shift.argtypes=[ctypes.c_void_p,ctypes.c_uint8];cls.lib.open_cfw_cordio_sec_cmac_shift.restype=ctypes.c_uint8
  cls.lib.open_cfw_cordio_sec_ecc_secret.argtypes=[ctypes.c_void_p,ctypes.c_uint8,ctypes.c_uint16,ctypes.c_uint8];cls.lib.open_cfw_cordio_sec_ecc_secret.restype=ctypes.c_uint8
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def setUp(self):self.lib.host_sec_reset();self.lib.open_cfw_cordio_sec_init();self.lib.open_cfw_cordio_sec_aes_init();self.lib.open_cfw_cordio_sec_cmac_init();self.lib.open_cfw_cordio_sec_ecc_init()
 def u32(self,n):return ctypes.c_uint32.in_dll(self.lib,n).value
 def array(self,n,s):return (ctypes.c_uint8*s).in_dll(self.lib,n)
 def test_random_ring_and_refill(self):
  state=(ctypes.c_uint8*128).in_dll(self.lib,"host_sec_state_storage");state[:32]=range(32);state[58]=3;out=(ctypes.c_uint8*10)();self.lib.open_cfw_cordio_sec_random(out,10)
  self.assertEqual(list(out),list(range(24,32))+[0,1]);self.assertEqual(self.u32("host_sec_random_requests"),2);self.assertEqual(state[58],1)
 def test_aes_queue_completion(self):
  key=(ctypes.c_uint8*16)(*range(16));text=(ctypes.c_uint8*16)(*range(16,32));token=self.lib.open_cfw_cordio_sec_aes(key,text,7,0x1234,0x55)
  self.assertEqual(token,0);self.assertEqual(self.u32("host_sec_encrypt_requests"),1)
  event=(ctypes.c_uint8*21)();event[2]=0x1B;event[5:21]=range(32,48);self.lib.host_sec_emit(event)
  self.assertEqual(self.u32("host_sec_send_count"),1)
 def test_cmac_shift(self):
  value=(ctypes.c_uint8*16)();value[0]=0x80;self.assertEqual(self.lib.open_cfw_cordio_sec_cmac_shift(value,1),1);self.assertTrue(all(x==0 for x in value))
 def test_ecc_key_order_and_completion(self):
  key=(ctypes.c_uint8*64)(*range(64));self.assertEqual(self.lib.open_cfw_cordio_sec_ecc_secret(key,4,9,8),1)
  self.assertEqual(list(self.array("host_sec_last_dh_x",32)),list(reversed(range(32))));self.assertEqual(list(self.array("host_sec_last_dh_y",32)),list(reversed(range(32,64))))
  event=(ctypes.c_uint8*37)();event[2]=0x26;event[4]=0;event[5:37]=range(32);self.lib.host_sec_emit(event);self.assertEqual(self.u32("host_sec_send_count"),1)
 def test_all_isolated_target_entries_compile(self):
  with tempfile.TemporaryDirectory() as d:
   for n in range(1,21):subprocess.run(["/usr/bin/clang","--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-builtin","-Wall","-Wextra","-Werror",f"-DSEC_SELECTOR={n}","-c",str(SOURCE),"-o",str(Path(d)/f"{n}.o")],check=True)

if __name__=="__main__":unittest.main()
