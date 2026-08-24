import ctypes, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/apollo_main/core_overlay/service_ring_battery.c"
FIXTURE=ROOT/"tests/fixtures/service_ring_battery_host.c"
HEADER=ROOT/"tests/fixtures/service_ring_battery_host.h"
SELECTORS={
 "update":"OPEN_CFW_RING_BATTERY_UPDATE_ONLY",
 "state_set":"OPEN_CFW_RING_BATTERY_STATE_SET_ONLY",
 "level_get":"OPEN_CFW_RING_BATTERY_LEVEL_GET_ONLY",
 "charging_get":"OPEN_CFW_RING_BATTERY_CHARGING_GET_ONLY",
 "request":"OPEN_CFW_RING_BATTERY_REQUEST_ONLY",
}
class State(ctypes.Structure):_fields_=[("level",ctypes.c_uint8),("charging",ctypes.c_uint8)]
class ServiceRingBatteryCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.libs={}
  for name,selector in SELECTORS.items():
   out=Path(cls.temp.name)/(name+".so")
   subprocess.run(["/usr/bin/clang","-std=c11","-shared","-fPIC","-O2","-Wall","-Wextra","-Werror","-include",str(HEADER),"-D"+selector+"=1",str(SOURCE),str(FIXTURE),"-o",str(out)],check=True)
   cls.libs[name]=ctypes.CDLL(str(out))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_state_clamps_and_normalizes(self):
  lib=self.libs["state_set"];f=lib.open_cfw_ring_battery_state_set;f.argtypes=[ctypes.c_uint8,ctypes.c_uint8]
  f(101,9);s=State.in_dll(lib,"host_state");self.assertEqual((s.level,s.charging),(100,1))
  f(73,0);self.assertEqual((s.level,s.charging),(73,0))
 def test_accessors(self):
  for name,symbol,value in (("level_get","open_cfw_ring_battery_level_get",82),("charging_get","open_cfw_ring_battery_charging_get",1)):
   lib=self.libs[name];s=State.in_dll(lib,"host_state");s.level=82;s.charging=1;f=getattr(lib,symbol);f.restype=ctypes.c_uint8;self.assertEqual(f(),value)
 def test_update_message(self):
  lib=self.libs["update"];f=lib.open_cfw_ring_battery_update;f.argtypes=[ctypes.c_uint8,ctypes.c_uint8];f(61,7)
  msg=bytes((ctypes.c_uint8*12).in_dll(lib,"host_message"));self.assertEqual(msg[:4],bytes([5,8,0,0]));self.assertEqual(int.from_bytes(msg[4:8],"little"),61);self.assertEqual(msg[8],1);self.assertEqual((ctypes.c_uint16.in_dll(lib,"host_service").value,ctypes.c_uint16.in_dll(lib,"host_length").value,ctypes.c_uint8.in_dll(lib,"host_route").value),(0x105,12,1))
 def test_request_message(self):
  lib=self.libs["request"];lib.open_cfw_ring_battery_request_from_peer();msg=bytes((ctypes.c_uint8*12).in_dll(lib,"host_message"));self.assertEqual(msg,bytes([6])+bytes(11));self.assertEqual(ctypes.c_uint8.in_dll(lib,"host_route").value,2)
if __name__=="__main__":unittest.main()
