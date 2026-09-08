# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_dw_spi_probe import Case, expected, STATE, REGS

class ProbeModelTests(unittest.TestCase):
    def test_existing_depths_skip_probes(self):
        trace,depths=expected(Case(tx_depth=16,rx_depth=32))
        self.assertEqual(depths,(16,32))
        self.assertFalse(any(t[0]=='write' and t[1] in (REGS+24,REGS+28) for t in trace))

    def test_probe_boundaries(self):
        for mismatch,wanted,attempts in ((2,2,1),(16,16,15),(257,0,256),(0,258,256)):
            trace,depths=expected(Case(tx_mismatch=mismatch,rx_depth=16))
            self.assertEqual(depths[0],wanted)
            writes=[t for t in trace if t[0]=='write' and t[1]==REGS+24]
            self.assertEqual(len(writes),attempts+1)
            self.assertEqual(writes[-1],('write',REGS+24,0))

    def test_fifo_drain_and_busy_wait(self):
        trace,_=expected(Case(tx_depth=1,rx_depth=1,status=(8,9,0,1,1,0)))
        self.assertEqual(sum(t[0]=='read' and t[1]==REGS+96 for t in trace),2)
        self.assertEqual(trace[-1],('request_irq',16,0x10206170,STATE))

    def test_incomplete_hardware_script_fails(self):
        with self.assertRaisesRegex(ValueError,'completion'):
            expected(Case(status=(8,)))

    def test_unused_status_is_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError,'Unused'):
            expected(Case(status=(0,0,0)))

if __name__=='__main__': unittest.main()
