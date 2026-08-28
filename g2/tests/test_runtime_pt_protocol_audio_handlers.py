# SPDX-License-Identifier: MIT
from __future__ import annotations
import os,subprocess,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];I=R/"components/apollo_main/core_overlay";S=[I/"pt_protocol_procsr.c",I/"pt_protocol_handlers_audio.c"]
class Tests(unittest.TestCase):
 def test_compile(self):
  cc=os.environ.get("OPENCFW_CLANG","/usr/bin/clang")
  with tempfile.TemporaryDirectory() as d:
   for s in S:
    for t,f in (("h",["clang"]),("t",[cc,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-ffreestanding","-fno-builtin"])):subprocess.run(f+["-std=c11","-Oz","-Wall","-Wextra","-Werror","-I",str(I),"-c",str(s),"-o",str(Path(d)/(s.stem+t+".o"))],check=True,capture_output=True,text=True)
 def test_commands(self):
  x=(I/"pt_protocol_handlers_audio.c").read_text()
  for c in (0x18,0x19,0x1A,0x1B,0x1C):self.assertIn(f"{{0x{c:02X}U,",x)
  self.assertIn("uint8_t data[210]",x);self.assertIn("*l=220U",x)
if __name__=="__main__":unittest.main()
