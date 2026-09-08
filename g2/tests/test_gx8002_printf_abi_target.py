# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_printf_abi import execute

class PrintfAbiTests(unittest.TestCase):
    def test_restore_check_rejects_clobbered_return_address(self):
        code={0:('movi','r2, 36864',2),2:('bsr','0x100',4),6:('rts','',2)}
        with self.assertRaisesRegex(ValueError,'ABI restore mismatch'):
            execute(code,0,256,[],0)

    def test_wrong_call_rejected(self):
        with self.assertRaisesRegex(ValueError,'wrong formatter call'):
            execute({0:('bsr','0x102',4)},0,256,[],0)

if __name__=='__main__':unittest.main()
