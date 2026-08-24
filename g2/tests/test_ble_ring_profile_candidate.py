from __future__ import annotations
import ctypes,platform,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/apollo_main/core_overlay/ble_ring_profile.c';FIX=ROOT/'tests/fixtures'
class Msg(ctypes.Structure):
 _fields_=[('parameter',ctypes.c_uint16),('event',ctypes.c_uint8),('status',ctypes.c_uint8),('data',ctypes.POINTER(ctypes.c_uint8)),('length',ctypes.c_uint16),('handle',ctypes.c_uint16)]
class BleRingProfileCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/('ring'+('.dylib' if platform.system()=='Darwin' else '.so'))
  subprocess.run(['clang','-std=c11','-shared','-fPIC','-O1','-Wall','-Wextra','-Werror','-include',str(FIX/'ble_ring_profile_host.h'),str(SOURCE),str(FIX/'ble_ring_profile_host.c'),'-o',str(p)],check=True,cwd=ROOT);c.l=ctypes.CDLL(str(p));c.l.open_cfw_test_ring_word.argtypes=[ctypes.c_uint32];c.l.open_cfw_test_ring_word.restype=ctypes.c_uint32;c.l.open_cfw_test_ring_set.argtypes=[ctypes.c_uint32,ctypes.c_uint32];c.l.open_cfw_test_ring_handles.restype=ctypes.POINTER(ctypes.c_uint16);c.l.open_cfw_ring_handler_init.argtypes=[ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint16)];c.l.open_cfw_ring_service_discover.argtypes=[ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint16)];c.l.open_cfw_ring_pack_ccc_epoch.argtypes=[ctypes.c_uint8,ctypes.c_uint8,ctypes.c_uint16];c.l.open_cfw_ring_pack_ccc_epoch.restype=ctypes.c_uint32;c.l.open_cfw_ring_enable_ccc.argtypes=[ctypes.c_void_p];c.l.open_cfw_ring_process_message.argtypes=[ctypes.c_uint32,ctypes.POINTER(Msg)]
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def setUp(s):s.l.open_cfw_test_ring_reset()
 def w(s,i):return s.l.open_cfw_test_ring_word(i)
 def test_pack_init_and_discovery(s):
  h=s.l.open_cfw_test_ring_handles();s.assertEqual(s.l.open_cfw_ring_pack_ccc_epoch(2,1,0x3456),0x34560102);s.l.open_cfw_ring_handler_init(7,h);s.assertEqual(tuple(s.w(i) for i in range(6)),(0,7,1,0x10,0x12,0x13));s.l.open_cfw_ring_service_discover(2,h);s.assertEqual(tuple(s.w(i) for i in range(40,47)),(1,2,16,0x1f,3,1,1))
 def test_enable_ccc_epoch_and_final_event(s):
  s.l.open_cfw_test_ring_set(0,2);s.l.open_cfw_test_ring_set(2,9);s.l.open_cfw_test_ring_set(5,0x1234);p=(9<<16)|(1<<8)|2;s.l.open_cfw_ring_enable_ccc(ctypes.c_void_p(p));s.assertEqual(tuple(s.w(i) for i in range(6,14)),(1,2,1,1,2,0x1234,2,1));s.assertEqual((s.w(20),s.w(21)),(1,4));s.l.open_cfw_test_ring_set(2,10);s.l.open_cfw_ring_enable_ccc(ctypes.c_void_p(p));s.assertEqual(s.w(9),1)
 def test_open_and_close_epoch_schedules(s):
  s.l.open_cfw_ring_handler_init(6,s.l.open_cfw_test_ring_handles());m=Msg(parameter=3,event=0x27);s.l.open_cfw_ring_process_message(0,ctypes.byref(m));s.assertEqual(tuple(s.w(i) for i in range(6)),(3,6,2,0x10,0x12,0x13));s.assertEqual((s.w(17),s.w(18),s.w(51),s.w(52),s.w(53)),(1,3,500,700,900));s.assertEqual((s.w(48),s.w(49),s.w(50)),(0x00020003,0x00020003,0x00020103));m.event=0x28;s.l.open_cfw_ring_process_message(0,ctypes.byref(m));s.assertEqual(tuple(s.w(i) for i in range(6)),(0,6,3,0,0,0));s.assertEqual((s.w(17),s.w(20),s.w(21)),(2,1,8))
 def test_receive_and_send_dispatch(s):
  d=(ctypes.c_uint8*2)(0x41,0x42);s.l.open_cfw_ring_handler_init(5,s.l.open_cfw_test_ring_handles());s.l.open_cfw_test_ring_set(0,2);m=Msg(event=0x0d,status=0,data=d,length=2,handle=0x12);s.l.open_cfw_ring_process_message(0,ctypes.byref(m));s.assertEqual((s.w(22),s.w(23),s.w(24)),(1,2,0x41));m=Msg(parameter=2,event=0xac,data=d,length=2);s.l.open_cfw_ring_process_message(0,ctypes.byref(m));s.assertEqual((s.w(25),s.w(26),s.w(27),s.w(28),s.w(29)),(1,2,0x10,2,0x41));m.parameter=3;s.l.open_cfw_ring_process_message(0,ctypes.byref(m));s.assertEqual(s.w(38),1)
 def test_send_queue_and_alloc_failure(s):
  d=(ctypes.c_uint8*1)(0x55);s.assertEqual(s.l.open_cfw_ring_send_data(d,1),0);s.assertEqual(s.w(30),0);s.l.open_cfw_ring_handler_init(9,s.l.open_cfw_test_ring_handles());s.l.open_cfw_test_ring_set(0,2);s.l.open_cfw_ring_send_data(d,1);s.assertEqual((s.w(30),s.w(31),s.w(32),s.w(33),s.w(34),s.w(35),s.w(36),s.w(37)),(1,1,12,1,9,2,0xac,1));s.l.open_cfw_test_ring_set(39,1);s.l.open_cfw_ring_send_data(d,1);s.assertEqual(s.w(38),1)
 def test_selectors(s):
  sels={'PACK':'open_cfw_ring_pack_ccc_epoch','ENABLE_CCC':'open_cfw_ring_enable_ccc','INIT':'open_cfw_ring_handler_init','DISCOVER':'open_cfw_ring_service_discover','RECEIVE':'open_cfw_ring_receive_data','PROCESS':'open_cfw_ring_process_message','SEND':'open_cfw_ring_send_data'};flags=['-target','thumbv7em-none-eabi','-mthumb','-O2','-ffreestanding','-fno-jump-tables','-fomit-frame-pointer','-fno-builtin','-mno-unaligned-access','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
  with tempfile.TemporaryDirectory() as d:
   for k,v in sels.items():
    o=Path(d)/(k+'.o');subprocess.run(['clang',*flags,f'-DOPEN_CFW_RING_{k}_ONLY=1','-c',str(SOURCE),'-o',str(o)],check=True,cwd=ROOT);out=subprocess.run(['nm',str(o)],check=True,capture_output=True,text=True).stdout;got={p[2] for l in out.splitlines() if len(p:=l.split())==3 and p[1]=='T'};s.assertEqual(got,{v})
if __name__=='__main__':unittest.main()
