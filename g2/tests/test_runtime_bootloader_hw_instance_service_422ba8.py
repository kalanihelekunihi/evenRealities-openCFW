from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_instance_service_422ba8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_instance_service_host.c"
SIZE = 0x11C


class BootloaderHardwareInstanceServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hw-service.dylib" if sys.platform == "darwin" else "hw-service.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.service = cls.lib.open_cfw_bootloader_hw_instance_service_422ba8
        cls.service.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
        cls.service.restype = ctypes.c_uint32
        cls.reset = cls.lib.open_cfw_hws_host_reset
        cls.registers = ((ctypes.c_uint32 * 32) * 4).in_dll(cls.lib, "open_cfw_hws_host_registers")
        cls.events = ((ctypes.c_uint32 * 3) * 16).in_dll(cls.lib, "open_cfw_hws_host_events")
        cls.event_count = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hws_host_event_count")
        cls.revision = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hws_host_revision")
        cls.clock = ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hws_host_clock")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def put32(raw, offset, value):
        raw[offset:offset + 4] = int(value & 0xFFFFFFFF).to_bytes(4, "little")

    @staticmethod
    def get32(raw, offset):
        return int.from_bytes(bytes(raw[offset:offset + 4]), "little")

    def instance(self, index=0, active=1, mode=6, timestamp=0x16E361):
        raw = (ctypes.c_uint8 * SIZE)()
        self.put32(raw, 0, 0x01EA9E06)
        raw[4] = active
        self.put32(raw, 0x28, index)
        self.put32(raw, 0x30, timestamp)
        raw[0x118] = mode
        return raw

    def observed_events(self):
        return [tuple(self.events[i]) for i in range(self.event_count.value)]

    def test_authenticated_body_callers_literals_and_successor(self):
        blob = OFFICIAL.read_bytes()
        body = blob[0x12BA8:0x12D20]
        self.assertEqual(len(body), 376)
        self.assertEqual(hashlib.sha256(body).hexdigest(), "983a7c399b4e7e44e7e6c49d2da6112709588c7f005820cc5cf2a4a0a82300d4")
        self.assertEqual(blob[0x0F66E:0x0F672].hex(), "03f09bfa")
        self.assertEqual(blob[0x0F86C:0x0F870].hex(), "03f09cf9")
        self.assertEqual(blob[0x0F912:0x0F916].hex(), "03f049f9")
        self.assertEqual(tuple(int.from_bytes(blob[o:o + 4], "little") for o in (0x13434, 0x13438, 0x1343C, 0x13440)), (0x16E361, 0x4002000C, 0x400201B0, 0x40039000))
        self.assertEqual(blob[0x12D20:0x12D24].hex(), "806adff8")

    def test_validation_statuses_and_action_zero_short_paths(self):
        self.reset()
        self.assertEqual(self.service(None, 0, 1), 2)
        bad = self.instance(); self.put32(bad, 0, 0)
        self.assertEqual(self.service(bad, 0, 1), 2)
        good = self.instance()
        self.assertEqual(self.service(good, 3, 1), 6)
        good[4] = 0
        self.assertEqual(self.service(good, 0, 1), 7)
        self.assertEqual(self.observed_events(), [])
        self.assertEqual(self.service(good, 0, 0), 0)
        self.assertEqual(self.observed_events(), [(1, 11, 0)])

    def test_write_action_transfers_fields_routes_and_sets_clock_gate(self):
        for index in range(4):
            self.reset(); self.revision.value = 0x122; self.clock.value = 0x80000000
            raw = self.instance(index=index, active=1, mode=4 + index)
            values = [0xA5000000 + index * 0x100 + i for i in range(8)]
            for i, value in enumerate(values): self.put32(raw, 8 + 4 * i, value)
            self.assertEqual(self.service(raw, 0, 1), 0)
            self.assertEqual(list(self.registers[index][:7]), values[:7])
            self.assertEqual(self.registers[index][18], values[7])
            self.assertEqual(raw[4], 0)
            self.assertEqual(self.clock.value, 0x80000000 | (0x00400000 << index))
            self.assertEqual(self.observed_events(), [(1, 11 + index, 0), (2, 4 + index, 11 + index)])

    def test_read_actions_copy_fields_clear_gate_and_teardown_in_order(self):
        for action in (1, 2):
            self.reset(); index = action; self.revision.value = 0x22
            self.clock.value = 0xFFFFFFFF
            raw = self.instance(index=index, active=0, mode=9)
            values = [0x5A000000 + action * 0x100 + i for i in range(32)]
            for i, value in enumerate(values): self.registers[index][i] = value
            self.assertEqual(self.service(raw, action, 1), 0)
            self.assertEqual([self.get32(raw, 8 + 4 * i) for i in range(7)], values[:7])
            self.assertEqual(self.get32(raw, 0x24), values[18])
            self.assertEqual(raw[4], 1)
            self.assertEqual(self.registers[index][4], 0)
            self.assertEqual(self.clock.value, 0xFFFFFFFF & ~(0x00400000 << index))
            events = self.observed_events()
            self.assertEqual(events[0], (3, 9, 11 + index))
            self.assertEqual(events[1][0], 4)
            self.assertEqual(events[1][2], 0xFFFFFFFF)
            self.assertEqual(events[2], (5, 11 + index, 0))

    def test_thresholds_and_no_copy_teardown(self):
        self.reset(); raw = self.instance(index=3, timestamp=0x16E360)
        self.clock.value = 0xFFFFFFFF; self.revision.value = 0x21
        sentinel = bytes(raw)
        self.assertEqual(self.service(raw, 1, 0), 0)
        self.assertEqual(bytes(raw), sentinel)
        self.assertEqual(self.clock.value, 0xFFFFFFFF)
        self.assertEqual([row[0] for row in self.observed_events()], [3, 4, 5])

    def test_source_cross_compiles(self):
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hw-service.o"))], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
