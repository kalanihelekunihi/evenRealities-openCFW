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
FIXTURE = ROOT / "tests/fixtures/bootloader_gate_state_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_gate_state.c"


class BootloaderGateStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-gate-state.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"),
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_gate_state_set.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_gate_state.restype = ctypes.c_uint
        cls.lib.open_cfw_test_gate_state_calls.restype = ctypes.c_uint
        cls.lib.open_cfw_test_gate_state_reads.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, state: int, gate: int) -> tuple[int, int, int]:
        self.lib.open_cfw_test_gate_state_set(state, gate)
        result = self.lib.open_cfw_bootloader_gate_state()
        return (
            result,
            self.lib.open_cfw_test_gate_state_calls(),
            self.lib.open_cfw_test_gate_state_reads(),
        )

    def test_authenticated_complete_stock_entry_and_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x6088:0x60B0]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            40,
            "0fb1ec985d7caf9e9575909ee1fcf3c7c7941be48737826c41c28d29b266bc87",
        ))
        callers = []
        for offset in range(0, len(image) - 3, 2):
            first = int.from_bytes(image[offset:offset + 2], "little")
            second = int.from_bytes(image[offset + 2:offset + 4], "little")
            if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
                continue
            sign = (first >> 10) & 1
            i1 = 1 ^ ((second >> 13) & 1) ^ sign
            i2 = 1 ^ ((second >> 11) & 1) ^ sign
            immediate = (
                (sign << 24) | (i1 << 23) | (i2 << 22)
                | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
            )
            if immediate & (1 << 24):
                immediate -= 1 << 25
            if 0x00410000 + offset + 4 + immediate == 0x00416088:
                callers.append(0x00410000 + offset)
        self.assertEqual(callers, [0x004207CC])

    def test_state_mapping_and_gate_read_short_circuits(self) -> None:
        self.assertEqual(self.run_case(0, 0), (3, 1, 0))
        self.assertEqual(self.run_case(0, 1), (3, 1, 0))
        self.assertEqual(self.run_case(2, 0), (2, 1, 0))
        self.assertEqual(self.run_case(2, 1), (2, 1, 0))
        self.assertEqual(self.run_case(1, 1), (1, 1, 1))
        self.assertEqual(self.run_case(1, 0), (0, 1, 1))
        self.assertEqual(self.run_case(3, 1), (1, 1, 1))
        self.assertEqual(self.run_case(3, 2), (0, 1, 1))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "gate-state.o"
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
