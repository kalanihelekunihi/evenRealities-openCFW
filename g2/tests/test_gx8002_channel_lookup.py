# SPDX-License-Identifier: MIT
import subprocess
import unittest
from verify_gx8002_channel_lookup import ROOT, decode, execute


class ChannelLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
        cls.code = decode(subprocess.check_output([pre, '-D', '--start-address=0x1104c',
            '--stop-address=0x11068', str(ROOT/'build/gx8002-board/padmux-get-stock.elf')], text=True))

    def test_distinct_valid_channels(self):
        self.assertEqual(execute(self.code, 0x1104c, 0), 0x2002e050)
        self.assertEqual(execute(self.code, 0x1104c, 1), 0x2002e1cc)

    def test_every_other_byte_rejected(self):
        for channel in range(2, 256):
            self.assertEqual(execute(self.code, 0x1104c, channel), 0)

    def test_lookup_itself_does_not_truncate_argument(self):
        for channel in (256, 257, 0xffffff00, 0xffffff01):
            self.assertEqual(execute(self.code, 0x1104c, channel), 0)

    def test_changed_rejection_predicate_detectable(self):
        mutated = dict(self.code)
        op, args, width = mutated[0x11050]
        self.assertEqual((op, args), ('cmpnei', 'r0, 1'))
        mutated[0x11050] = (op, 'r0, 255', width)
        self.assertNotEqual(execute(mutated, 0x1104c, 255), 0)
