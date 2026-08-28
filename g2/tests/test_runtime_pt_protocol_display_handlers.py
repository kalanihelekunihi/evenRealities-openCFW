# SPDX-License-Identifier: MIT
from __future__ import annotations
import os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];I=ROOT/"components/apollo_main/core_overlay"
S=[I/"pt_protocol_procsr.c",I/"pt_protocol_handlers_display.c"]
class PtProtocolDisplayHandlersTests(unittest.TestCase):
 def test_compile(self):
  cc=os.environ.get("OPENCFW_CLANG","/usr/bin/clang")
  with tempfile.TemporaryDirectory(prefix="g2-pt-display-") as d:
   for src in S:
    for tag,flags in (("h",["clang"]),("t",[cc,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-ffreestanding","-fno-builtin"])):
     subprocess.run(flags+["-std=c11","-Oz","-Wall","-Wextra","-Werror","-I",str(I),"-c",str(src),"-o",str(Path(d)/(src.stem+tag+".o"))],check=True,capture_output=True,text=True)
 def test_commands(self):
  text=(I/"pt_protocol_handlers_display.c").read_text()
  for c in (0x20,0x22,0x2D,0x2E,0x3E,0x6E,0x74,0x75,0x77):self.assertIn(f"{{0x{c:02X}U,",text)
  for screen in ("0x010BU","0x010FU","0x0110U"):self.assertIn(screen,text)
if __name__=="__main__":unittest.main()
