from __future__ import annotations
import ctypes,platform,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/apollo_main/core_overlay/ble_ota_profile.c';FIX=ROOT/'tests/fixtures'
class Msg(ctypes.Structure):
 _fields_=[('parameter',ctypes.c_uint16),('event',ctypes.c_uint8),('status',ctypes.c_uint8),('data',ctypes.POINTER(ctypes.c_uint8)),('length',ctypes.c_uint16),('reserved',ctypes.c_uint16)]
class Ccc(ctypes.Structure):
 _fields_=[('parameter',ctypes.c_uint16),('event',ctypes.c_uint8),('status',ctypes.c_uint8),('handle',ctypes.c_uint16),('value',ctypes.c_uint16),('index',ctypes.c_uint8)]
class BleOtaProfileCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/('ota'+('.dylib' if platform.system()=='Darwin' else '.so'))
  subprocess.run(['clang','-std=c11','-shared','-fPIC','-O1','-Wall','-Wextra','-Werror','-include',str(FIX/'ble_ota_profile_host.h'),str(SOURCE),str(FIX/'ble_ota_profile_host.c'),'-o',str(p)],check=True,cwd=ROOT);c.l=ctypes.CDLL(str(p));c.l.open_cfw_test_ota_word.argtypes=[ctypes.c_uint32];c.l.open_cfw_test_ota_word.restype=ctypes.c_uint32;c.l.open_cfw_test_ota_set.argtypes=[ctypes.c_uint32,ctypes.c_uint32];c.l.open_cfw_ota_process_message.argtypes=[ctypes.POINTER(Msg)];c.l.open_cfw_ota_process_ccc.argtypes=[ctypes.c_void_p]
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def setUp(s):s.l.open_cfw_test_ota_reset()
 def w(s,i):return s.l.open_cfw_test_ota_word(i)
 def test_init_and_ccc(s):
  s.l.open_cfw_ota_handler_init(9);s.assertEqual(tuple(s.w(i) for i in range(4)),(0,9,0,0));s.assertEqual(s.w(19),1)
  m=Ccc(parameter=2,event=0x14,index=1,value=1);s.l.open_cfw_ota_process_ccc(ctypes.byref(m));s.assertEqual((s.w(0),s.w(2)),(2,1));m.value=0;s.l.open_cfw_ota_process_ccc(ctypes.byref(m));s.assertEqual((s.w(0),s.w(2)),(0,0))
 def test_dispatch(s):
  m=Msg(event=0x12,status=0);s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual(s.w(3),1);m.status=1;s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual(s.w(3),0)
  m.event=0xA0;s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual((s.w(7),s.w(8),s.w(9)),(1,0,0))
  s.l.open_cfw_test_ota_set(0,3);m.event=0xA1;s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual((s.w(10),s.w(11),s.w(12),s.w(15)),(1,3,1,200))
  s.l.open_cfw_test_ota_set(4,1);m=Msg(parameter=3,event=0x28);s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual((s.w(0),s.w(16),s.w(17)),(0,1,3))
 def test_send_and_notify(s):
  d=(ctypes.c_uint8*3)(0x41,0x42,0x43);s.assertEqual(s.l.open_cfw_ota_send_data(d,3),0);s.assertEqual((s.w(20),s.w(21)),(1,0))
  s.l.open_cfw_test_ota_set(0,2);s.l.open_cfw_test_ota_set(1,7);s.l.open_cfw_test_ota_set(2,1);s.l.open_cfw_ota_send_data(d,3);s.assertEqual((s.w(20),s.w(21),s.w(23),s.w(24),s.w(25),s.w(26),s.w(27),s.w(28),s.w(30)),(2,1,1,12,1,7,2,0xA7,3));m=Msg(parameter=2,event=0xA7,data=d,length=3);s.l.open_cfw_ota_process_message(ctypes.byref(m));s.assertEqual((s.w(3),s.w(31),s.w(32),s.w(33),s.w(34)),(0,1,2,0x824,3))
 def test_alloc_failure_and_write(s):
  d=(ctypes.c_uint8*1)(0x55);s.l.open_cfw_test_ota_set(0,1);s.l.open_cfw_test_ota_set(2,1);s.l.open_cfw_test_ota_set(5,1);s.l.open_cfw_ota_send_data(d,1);s.assertEqual(s.w(22),1)
  s.l.open_cfw_ota_write_callback.argtypes=[ctypes.c_uint8,ctypes.c_uint16,ctypes.c_uint8,ctypes.c_uint16,ctypes.c_uint16,ctypes.POINTER(ctypes.c_uint8),ctypes.c_void_p];s.assertEqual(s.l.open_cfw_ota_write_callback(1,2,3,4,1,d,None),0);s.assertEqual((s.w(4),s.w(5),s.w(6)),(1,1,0x55))
 def test_selectors(s):
  sels={'CCC':'open_cfw_ota_process_ccc','PROCESS':'open_cfw_ota_process_message','WRITE':'open_cfw_ota_write_callback','INIT':'open_cfw_ota_handler_init','DISCONNECT':'open_cfw_ota_disconnect','PUBLIC_PROCESS':'open_cfw_ota_public_process_message','SEND':'open_cfw_ota_send_data'};flags=['-target','thumbv7em-none-eabi','-mthumb','-O2','-ffreestanding','-fno-jump-tables','-fomit-frame-pointer','-fno-builtin','-mno-unaligned-access','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
  with tempfile.TemporaryDirectory() as d:
   for k,v in sels.items():
    o=Path(d)/(k+'.o');subprocess.run(['clang',*flags,f'-DOPEN_CFW_OTA_{k}_ONLY=1','-c',str(SOURCE),'-o',str(o)],check=True,cwd=ROOT);out=subprocess.run(['nm',str(o)],check=True,capture_output=True,text=True).stdout;got={p[2] for l in out.splitlines() if len(p:=l.split())==3 and p[1]=='T'};s.assertEqual(got,{v})
if __name__=='__main__':unittest.main()
