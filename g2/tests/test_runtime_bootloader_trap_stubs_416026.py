from __future__ import annotations

import hashlib
import re
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_trap_stubs_416026.c"

FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


class BootloaderTrapStubTests(unittest.TestCase):
    """Both stubs are single-instruction, no-state Thumb-2 bodies (an
    infinite self-loop trap and a no-op return). Neither has meaningful
    dynamic behavior to execute on the host -- the infinite loop cannot run
    at all, and the no-op return has no observable effect -- so this suite
    verifies them statically: the retained stock bytes, and that the
    reviewed C compiles for Cortex-M55 to the exact same bytes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.object_path = Path(cls.temporary.name) / "trap_stubs.o"
        subprocess.run(
            ["/usr/bin/clang", *FLAGS, "-c", str(SOURCE), "-o", str(cls.object_path)],
            check=True, capture_output=True,
        )
        disassembly = subprocess.run(
            [
                "/Applications/Xcode.app/Contents/Developer/Toolchains/"
                "XcodeDefault.xctoolchain/usr/bin/llvm-objdump",
                "-d", str(cls.object_path),
            ],
            check=True, capture_output=True, text=True,
        ).stdout
        cls.disassembly = disassembly

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_bodies(self) -> None:
        blob = OFFICIAL.read_bytes()
        trap = blob[0x6026:0x6028]
        noop = blob[0x6028:0x602A]
        self.assertEqual(trap.hex(), "fee7")
        self.assertEqual(noop.hex(), "7047")
        self.assertEqual(
            hashlib.sha256(trap).hexdigest(),
            "575fc8fa9e92ffe7d57a6aef6f1168f39da04f07d6bcd5b5e17883bff7b33165",
        )
        self.assertEqual(
            hashlib.sha256(noop).hexdigest(),
            "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
        )

    def test_trap_compiles_to_self_branch(self) -> None:
        # capstone-free structural check: a naked one-instruction function
        # whose body is exactly the two-byte unconditional self-branch.
        section = re.search(
            r"<open_cfw_bootloader_runtime_trap_416026>:\n(.*?)\n\n",
            self.disassembly, re.S,
        )
        self.assertIsNotNone(section)
        lines = [line for line in section.group(1).splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("e7fe", lines[0])
        self.assertIn("b\t0x0 <open_cfw_bootloader_runtime_trap_416026>", lines[0])

    def test_noop_return_compiles_to_bx_lr(self) -> None:
        section = re.search(
            r"<open_cfw_bootloader_runtime_noop_return_416028>:\n(.*)",
            self.disassembly, re.S,
        )
        self.assertIsNotNone(section)
        lines = [line for line in section.group(1).splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("4770", lines[0])
        self.assertIn("bx\tlr", lines[0])


if __name__ == "__main__":
    unittest.main()
