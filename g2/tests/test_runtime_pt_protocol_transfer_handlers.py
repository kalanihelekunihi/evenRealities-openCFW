# SPDX-License-Identifier: MIT
from __future__ import annotations
import os,subprocess,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];I=R/"components/apollo_main/core_overlay";S=[I/"pt_protocol_procsr.c",I/"pt_protocol_handlers_transfer.c"]
class Tests(unittest.TestCase):
 def test_compile(self):
  cc=os.environ.get("OPENCFW_CLANG","/usr/bin/clang")
  with tempfile.TemporaryDirectory() as d:
   for s in S:
    for t,f in (("h",["clang"]),("t",[cc,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections"])):subprocess.run(f+["-std=c11","-Oz","-Wall","-Wextra","-Werror","-I",str(I),"-c",str(s),"-o",str(Path(d)/(s.stem+t+".o"))],check=True,capture_output=True,text=True)
 def test_complete_transfer_command_set(self):
  x=(I/"pt_protocol_handlers_transfer.c").read_text()
  for c in (0x2A,0x52,0x53,0x54,0x55,0x58,0x59,0x5A,0x5B,0x60):self.assertIn(f"{{0x{c:02X}U,",x)
  h=(I/"pt_protocol_handlers_transfer.h").read_text();self.assertIn("uint8_t *staging",h);self.assertIn("size_t staging_capacity",h);self.assertNotIn("uint8_t staging[6000]",h);self.assertIn("0x1021U",x)
if __name__=="__main__":unittest.main()
