from __future__ import annotations

import ctypes, platform, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/apollo_main/core_overlay/at_buzzer.c"
FIXTURE=ROOT/"tests/fixtures"

class AtBuzzerCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();suffix=".dylib" if platform.system()=="Darwin" else ".so";cls.libpath=Path(cls.temp.name)/("at_buzzer"+suffix)
  subprocess.run(["clang","-std=c11","-shared","-fPIC","-O1","-include",str(FIXTURE/"at_buzzer_host.h"),str(SOURCE),str(FIXTURE/"at_buzzer_host.c"),"-o",str(cls.libpath)],check=True,cwd=ROOT)
  cls.lib=ctypes.CDLL(str(cls.libpath));cls.lib.open_cfw_at_buzzer_test.argtypes=[ctypes.c_char_p];cls.lib.open_cfw_at_buzzer_test.restype=ctypes.c_int
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def setUp(self):self.lib.open_cfw_test_at_buzzer_reset()
 def call(self,value):return self.lib.open_cfw_at_buzzer_test(value)
 def count(self,name):return ctypes.c_uint.in_dll(self.lib,name).value
 def args(self):return list((ctypes.c_uint*3).in_dll(self.lib,"open_cfw_test_at_buzzer_arguments"))
 def output(self):return bytes((ctypes.c_char*2048).in_dll(self.lib,"open_cfw_test_at_buzzer_output")).split(b"\0",1)[0]
 def test_null_and_unknown_diagnostics(self):
  self.assertEqual(self.call(None),0);self.assertEqual(self.count("open_cfw_test_at_buzzer_output_count"),6);self.assertTrue(self.output().startswith(b"AT^BUZZER: Missing parameters\r\nUsage:\r\n"))
  self.setUp();self.assertEqual(self.call(b"wat,1"),0);self.assertEqual(self.output(),b"AT^BUZZER: Unknown subcommand 'wat'\r\nUse: note, play, start, stop\r\n")
 def test_note_success_missing_parse_and_bounds(self):
  self.assertEqual(self.call(b"note,7,3,100"),1);self.assertEqual(self.args(),[7,3,100]);self.assertEqual(self.count("open_cfw_test_at_buzzer_note_count"),1);self.assertEqual(self.output(),b"Buzzer note: 7, tone: 3, beat: 100\r\nAT^BUZZER+OK\r\n")
  for value,prefix in [(b"note",b"AT^BUZZER=note: Missing"),(b"note,1,x,2",b"AT^BUZZER=note: Invalid parameters (parsed 1)"),(b"note,8,0,1",b"AT^BUZZER=note: Parameters out of range"),(b"note,-1,0,1",b"AT^BUZZER=note: Parameters out of range")]:
   self.setUp();self.assertEqual(self.call(value),0);self.assertTrue(self.output().startswith(prefix));self.assertEqual(self.count("open_cfw_test_at_buzzer_note_count"),0)
 def test_play_preserves_atoi_zero_and_range(self):
  self.assertEqual(self.call(b"play,nondigit"),1);self.assertEqual(self.args()[0],0);self.assertEqual(self.count("open_cfw_test_at_buzzer_play_count"),1)
  for value in (b"play,11",b"play,-1"):
   self.setUp();self.assertEqual(self.call(value),0);self.assertEqual(self.count("open_cfw_test_at_buzzer_play_count"),0)
 def test_start_and_stop(self):
  self.assertEqual(self.call(b"start,20000,100"),1);self.assertEqual(self.args()[:2],[20000,100]);self.assertEqual(self.count("open_cfw_test_at_buzzer_start_count"),1)
  for value in (b"start",b"start,1",b"start,0,0",b"start,20001,0",b"start,1,101"):
   self.setUp();self.assertEqual(self.call(value),0);self.assertEqual(self.count("open_cfw_test_at_buzzer_start_count"),0)
  self.setUp();self.assertEqual(self.call(b"stop,ignored"),1);self.assertEqual(self.count("open_cfw_test_at_buzzer_stop_count"),1);self.assertEqual(self.output(),b"Buzzer stop\r\nAT^BUZZER+OK\r\n")
 def test_stock_prefix_matching_and_bounded_unknown_echo(self):
  self.assertEqual(self.call(b"note-extra,1,2,3"),1);self.assertEqual(self.args(),[1,2,3]);self.setUp();self.assertEqual(self.call(b"abcdefghijklmnopq,1"),0);self.assertIn(b"'abcdefghijklmno'",self.output())
 def test_thumb_compile_surface(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/"x.o";subprocess.run(["clang","-target","thumbv7em-none-eabi","-mthumb","-O2","-ffreestanding","-fno-jump-tables","-fomit-frame-pointer","-fno-builtin","-mno-unaligned-access","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fropi","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(target)],check=True,cwd=ROOT)
   symbols=subprocess.run(["nm",str(target)],check=True,capture_output=True,text=True).stdout;observed={f[2] for line in symbols.splitlines() if len(f:=line.split())==3 and f[1]=="T"};self.assertEqual(observed,{"open_cfw_at_buzzer_test"})

if __name__=="__main__":unittest.main()
