# SPDX-License-Identifier: MIT
from __future__ import annotations
import os, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INCLUDE=ROOT/"components/apollo_main/core_overlay"
SOURCES=[INCLUDE/"pt_protocol_procsr.c",INCLUDE/"pt_protocol_handlers_sensors.c"]

class PtProtocolSensorHandlersTests(unittest.TestCase):
    def test_strict_host_and_target_compile(self):
        cc=os.environ.get("OPENCFW_CLANG","/usr/bin/clang")
        with tempfile.TemporaryDirectory(prefix="g2-pt-sensor-") as d:
            for source in SOURCES:
                for name,flags in (("h",["clang"]),("t",[cc,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb","-ffreestanding","-fno-builtin"])):
                    subprocess.run(flags+["-std=c11","-Oz","-Wall","-Wextra","-Werror","-I",str(INCLUDE),"-c",str(source),"-o",str(Path(d)/(source.stem+name+".o"))],check=True,capture_output=True,text=True)

    def test_all_five_evidenced_commands_are_bound(self):
        text=(INCLUDE/"pt_protocol_handlers_sensors.c").read_text()
        for command in (0x13,0x17,0x43,0x47,0x48):
            self.assertIn(f"{{0x{command:02X}U,",text)
        self.assertIn(
            "physical qualification is blocked by unavailable physical", text)

if __name__=="__main__": unittest.main()
