from __future__ import annotations
import ctypes,platform,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'components/apollo_main/core_overlay/callback_facades.c';FIX=ROOT/'tests/fixtures'
class CallbackFacadesCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();p=Path(c.t.name)/('callback_facades'+('.dylib' if platform.system()=='Darwin' else '.so'))
  subprocess.run(['clang','-std=c11','-shared','-fPIC','-O1','-Wall','-Wextra','-Werror','-include',str(FIX/'callback_facades_host.h'),str(SOURCE),str(FIX/'callback_facades_host.c'),'-o',str(p)],check=True,cwd=ROOT);c.l=ctypes.CDLL(str(p));c.l.open_cfw_test_callback_word.argtypes=[ctypes.c_uint32];c.l.open_cfw_test_callback_word.restype=ctypes.c_uint32;c.l.open_cfw_test_callback_set.argtypes=[ctypes.c_uint32,ctypes.c_uint32]
  for n in ('open_cfw_cb_charge_register','open_cfw_cb_msg_register'):getattr(c.l,n).argtypes=[ctypes.c_size_t];getattr(c.l,n).restype=ctypes.c_uint32
  for n in ('open_cfw_cb_charge_unregister','open_cfw_cb_msg_unregister'):getattr(c.l,n).argtypes=[ctypes.c_size_t]
  for n in ('open_cfw_cb_charge_notify','open_cfw_cb_msg_notify'):getattr(c.l,n).argtypes=[ctypes.c_uint32,ctypes.c_uint32];getattr(c.l,n).restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def setUp(s):s.l.open_cfw_test_callback_reset()
 def w(s,i):return s.l.open_cfw_test_callback_word(i)
 def test_init_and_deinit(s):
  s.l.open_cfw_cb_charge_init();s.assertEqual(tuple(s.w(i) for i in range(3)),(1,1,1));s.l.open_cfw_cb_msg_init();s.assertEqual(tuple(s.w(i) for i in range(3)),(2,2,1));s.l.open_cfw_cb_charge_deinit();s.assertEqual((s.w(3),s.w(4)),(1,1));s.l.open_cfw_cb_msg_deinit();s.assertEqual((s.w(3),s.w(4)),(2,2))
 def test_register_and_null(s):
  s.l.open_cfw_test_callback_set(8,0x45);s.assertEqual(s.l.open_cfw_cb_charge_register(0),0);s.assertEqual(s.w(5),0);s.assertEqual(s.l.open_cfw_cb_charge_register(0x1234),0x45);s.assertEqual(tuple(s.w(i) for i in range(5,8)),(1,1,0x1234));s.assertEqual(s.l.open_cfw_cb_msg_register(0x5678),0x45);s.assertEqual((s.w(5),s.w(6),s.w(7)),(2,2,0x5678))
 def test_unregister_and_null(s):
  s.l.open_cfw_cb_charge_unregister(0);s.assertEqual(s.w(9),0);s.l.open_cfw_cb_charge_unregister(0x1234);s.assertEqual((s.w(9),s.w(10),s.w(11)),(1,1,0x1234));s.l.open_cfw_cb_msg_unregister(0x5678);s.assertEqual((s.w(9),s.w(10),s.w(11)),(2,2,0x5678))
 def test_notify_in_out_value(s):
  s.l.open_cfw_test_callback_set(16,7);s.assertEqual(s.l.open_cfw_cb_charge_notify(3,10),17);s.assertEqual(tuple(s.w(i) for i in range(12,16)),(1,1,3,10));s.assertEqual(s.l.open_cfw_cb_msg_notify(9,20),27);s.assertEqual(tuple(s.w(i) for i in range(12,16)),(2,2,9,20))
 def test_selectors(s):
  sels={'CHARGE_INIT':'open_cfw_cb_charge_init','CHARGE_DEINIT':'open_cfw_cb_charge_deinit','CHARGE_REGISTER':'open_cfw_cb_charge_register','CHARGE_UNREGISTER':'open_cfw_cb_charge_unregister','CHARGE_NOTIFY':'open_cfw_cb_charge_notify','MSG_INIT':'open_cfw_cb_msg_init','MSG_DEINIT':'open_cfw_cb_msg_deinit','MSG_REGISTER':'open_cfw_cb_msg_register','MSG_UNREGISTER':'open_cfw_cb_msg_unregister','MSG_NOTIFY':'open_cfw_cb_msg_notify'};flags=['-target','thumbv7em-none-eabi','-mthumb','-O2','-ffreestanding','-fno-jump-tables','-fomit-frame-pointer','-fno-builtin','-mno-unaligned-access','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fropi','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
  with tempfile.TemporaryDirectory() as d:
   for k,v in sels.items():
    o=Path(d)/(k+'.o');subprocess.run(['clang',*flags,f'-DOPEN_CFW_CB_{k}_ONLY=1','-c',str(SOURCE),'-o',str(o)],check=True,cwd=ROOT);out=subprocess.run(['nm',str(o)],check=True,capture_output=True,text=True).stdout;got={p[2] for l in out.splitlines() if len(p:=l.split())==3 and p[1]=='T'};s.assertEqual(got,{v})
if __name__=='__main__':unittest.main()
