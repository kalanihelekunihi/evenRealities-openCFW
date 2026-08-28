# SPDX-License-Identifier: MIT
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pt_protocol_board_backend.c"
HEADER = ROOT / "components/apollo_main/core_overlay/pt_protocol_board_backend.h"
FIXTURE = ROOT / "tests/fixtures/pt_protocol_board_backend_host.c"
INCLUDE = ROOT / "components/apollo_main/core_overlay"


class PtProtocolBoardBackendTests(unittest.TestCase):
    def test_calls_table_lifetime_contract_is_explicit(self):
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("The caller owns calls.", header)
        self.assertIn("remain valid and immutable for the full", header)
        self.assertIn("lifetime of board and the platform backend", header)

    def test_host_behavior(self):
        cc = shutil.which("clang") or shutil.which("cc")
        self.assertIsNotNone(cc)
        with tempfile.TemporaryDirectory(prefix="g2-pt-board-host-") as raw:
            executable = Path(raw) / "board-host"
            subprocess.run([
                cc, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-I", str(INCLUDE), str(SOURCE), str(FIXTURE),
                "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True)

    def test_cortex_m55_and_m0plus_relocatable_links(self):
        cc = shutil.which("clang")
        ld = shutil.which("ld.lld") or shutil.which("lld")
        nm = shutil.which("llvm-nm") or shutil.which("nm")
        self.assertIsNotNone(cc)
        self.assertIsNotNone(ld)
        self.assertIsNotNone(nm)
        with tempfile.TemporaryDirectory(prefix="g2-pt-board-target-") as raw:
            for cpu in ("cortex-m55", "cortex-m0plus"):
                obj = Path(raw) / f"{cpu}.o"
                linked = Path(raw) / f"{cpu}-linked.o"
                subprocess.run([
                    cc, "--target=arm-none-eabi", f"-mcpu={cpu}", "-mthumb",
                    "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-Wall",
                    "-Wextra", "-Werror", "-I", str(INCLUDE), "-c",
                    str(SOURCE), "-o", str(obj),
                ], check=True, capture_output=True, text=True)
                subprocess.run(
                    [ld, "-r", "-o", str(linked), str(obj)], check=True,
                    capture_output=True, text=True)
                undefined = subprocess.run(
                    [nm, "-u", str(linked)], check=True,
                    capture_output=True, text=True).stdout.strip()
                self.assertEqual(undefined, "")


if __name__ == "__main__":
    unittest.main()
