from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FIXTURE = ROOT / "tests/fixtures/bootloader_gate_acquire_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_gate_acquire.c"


class BootloaderGateAcquireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-gate-acquire.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_gate_set.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.c_uint,
        ]
        cls.lib.open_cfw_bootloader_gate_acquire.restype = ctypes.c_int
        for name in (
            "open_cfw_test_gate_word",
            "open_cfw_test_gate_critical_calls",
            "open_cfw_test_gate_state_calls",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, critical: int, state: int, gate: int) -> tuple[int, int, int, int]:
        self.lib.open_cfw_test_gate_set(critical, state, gate)
        result = self.lib.open_cfw_bootloader_gate_acquire()
        return (
            result,
            self.lib.open_cfw_test_gate_word(),
            self.lib.open_cfw_test_gate_critical_calls(),
            self.lib.open_cfw_test_gate_state_calls(),
        )

    def test_authenticated_complete_stock_entry(self) -> None:
        body = OFFICIAL.read_bytes()[0x6058:0x6088]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            48,
            "805717a87092e08f4225a51f07e8c0d26de600cd697ca91f552be3abc70fcf61",
        ))

    def test_gate_contract_and_short_circuits(self) -> None:
        self.assertEqual(self.run_case(1, 1, 0), (-6, 0, 1, 0))
        self.assertEqual(self.run_case(0, 0, 0), (-1, 0, 1, 1))
        self.assertEqual(self.run_case(0, 1, 1), (-1, 1, 1, 1))
        self.assertEqual(self.run_case(0, 1, 0), (0, 1, 1, 1))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "gate-acquire.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
