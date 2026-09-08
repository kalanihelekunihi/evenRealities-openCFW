# SPDX-License-Identifier: MIT
import subprocess
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_software_frame import ROOT, build, decode, execute


class ObservedStack(dict):
    def __init__(self, corrupt=None):
        super().__init__()
        self.writes = []
        self.corrupt = corrupt

    def __setitem__(self, key, value):
        self.writes.append((key, value))
        super().__setitem__(key, value)

    def pop(self, key):
        value = super().pop(key)
        return value ^ 1 if key == self.corrupt else value


class ArchitectureIRQFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.code = decode(subprocess.check_output([
            str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),
            '-d', str(ROOT/'build/gx8002-irq/entry.elf')], text=True))

    def test_documented_memory_layout(self):
        stack = ObservedStack()
        execute(self.code, 0x10025574, 0, stack=stack, architecture=True)
        # Independent fixed address/value oracle for seed zero.
        self.assertEqual(stack.writes[:8], [
            (0x7ffc, 0x12345678), (0x7ff8, 0x87654321),
            (0x7ff4, 13*0x1020304), (0x7ff0, 12*0x1020304),
            (0x7fec, 3*0x1020304), (0x7fe8, 2*0x1020304),
            (0x7fe4, 0x1020304), (0x7fe0, 0)])
        self.assertEqual(stack, {})

    def test_corrupt_saved_volatile_register(self):
        with self.assertRaisesRegex(ValueError, 'volatile register restoration'):
            execute(self.code, 0x10025574, 0, stack=ObservedStack(0x7fe0), architecture=True)

    def test_corrupt_saved_return_pc(self):
        with self.assertRaisesRegex(ValueError, 'control register restoration'):
            execute(self.code, 0x10025574, 0, stack=ObservedStack(0x7ffc), architecture=True)


if __name__ == '__main__':
    unittest.main()
