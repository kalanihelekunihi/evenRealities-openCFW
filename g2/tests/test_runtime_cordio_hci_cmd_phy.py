#!/usr/bin/env python3
"""Behavior and target-compile tests for the Cordio HCI PHY wrappers."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_cmd_phy.c"
INCLUDE = ROOT / "components/shared/cordio"

HARNESS = r"""
#include <stdint.h>
#include <string.h>

static uint8_t command[16];
static uint16_t observed_opcode;
static uint8_t observed_length;
static unsigned allocations;
static unsigned sends;
static int fail_allocation;

uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t length) {
    ++allocations;
    observed_opcode = opcode;
    observed_length = length;
    memset(command, 0xa5, sizeof(command));
    return fail_allocation ? (uint8_t *)0 : command;
}
void hciCmdSend(uint8_t *buffer) { if (buffer == command) ++sends; }

void test_reset(int fail) {
    observed_opcode = 0;
    observed_length = 0;
    allocations = sends = 0;
    fail_allocation = fail;
    memset(command, 0, sizeof(command));
}
uint16_t test_opcode(void) { return observed_opcode; }
uint8_t test_length(void) { return observed_length; }
unsigned test_allocations(void) { return allocations; }
unsigned test_sends(void) { return sends; }
uint8_t test_byte(unsigned index) { return index < sizeof(command) ? command[index] : 0; }
"""


class CordioHciCmdPhyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        directory = Path(cls.tmp.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS)
        library = directory / "libhci_cmd_phy.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-shared", "-fPIC", "-I", str(INCLUDE),
                str(SOURCE), str(harness), "-o", str(library),
            ],
            check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.test_byte.argtypes = [ctypes.c_uint]
        cls.lib.test_byte.restype = ctypes.c_uint8

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def reset(self, fail: bool = False) -> None:
        self.lib.test_reset(int(fail))

    def payload(self, length: int) -> list[int]:
        return [self.lib.test_byte(index) for index in range(3, 3 + length)]

    def assert_command(self, opcode: int, payload: list[int]) -> None:
        self.assertEqual(self.lib.test_opcode(), opcode)
        self.assertEqual(self.lib.test_length(), len(payload))
        self.assertEqual(self.payload(len(payload)), payload)
        self.assertEqual(self.lib.test_allocations(), 1)
        self.assertEqual(self.lib.test_sends(), 1)

    def test_all_commands_and_allocation_failure(self) -> None:
        self.reset()
        self.lib.HciLeReadPhyCmd(0x1234)
        self.assert_command(0x2030, [0x34, 0x12])

        self.reset()
        self.lib.HciLeSetDefaultPhyCmd(3, 2, 4)
        self.assert_command(0x2031, [3, 2, 4])

        self.reset()
        self.lib.HciLeSetPhyCmd(0x5678, 1, 2, 4, 0x9abc)
        self.assert_command(0x2032, [0x78, 0x56, 1, 2, 4, 0xbc, 0x9a])

        for function, arguments in (
            (self.lib.HciLeReadPhyCmd, (1,)),
            (self.lib.HciLeSetDefaultPhyCmd, (1, 2, 3)),
            (self.lib.HciLeSetPhyCmd, (1, 2, 3, 4, 5)),
        ):
            self.reset(True)
            function(*arguments)
            self.assertEqual(self.lib.test_allocations(), 1)
            self.assertEqual(self.lib.test_sends(), 0)

    def test_cortex_m55_translation_unit_and_each_api_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for index, function in enumerate(
                ("HciLeReadPhyCmd", "HciLeSetDefaultPhyCmd", "HciLeSetPhyCmd")
            ):
                output = Path(directory) / f"{index}.o"
                subprocess.run(
                    [
                        "clang", "--target=thumbv7em-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-O2", "-ffreestanding", "-fno-builtin",
                        "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                        "-Werror", "-I", str(INCLUDE), "-c", str(SOURCE), "-o", str(output),
                    ],
                    check=True,
                )
                symbols = subprocess.run(
                    ["nm", "-g", str(output)], check=True, capture_output=True, text=True
                ).stdout
                self.assertIn(function, symbols)


if __name__ == "__main__":
    unittest.main()
