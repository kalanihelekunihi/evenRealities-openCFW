# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_rtc_isr as v

class RtcIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build();cls.code=v.decode((v.ROOT/'build/gx8002-board/rtc-isr-candidate.disassembly.txt').read_text())

    def test_no_callback_still_acknowledges(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,4,0,0xffffffff,7,3),
                         ([('read',0x20027b40,0),('read',0xa0003018,3)],0))

    def test_callback_result_survives_ack_read(self):
        args=(4,0x10207000,0x20030000,0xffffffff,0)
        self.assertEqual(v.execute(self.code,v.ADDRESS,*args),v.expected(*args))

    def test_wrong_ack_address_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='ld.w' and '0x18' in a)
        op,args,w=code[pc];code[pc]=(op,args.replace('0x18','0x14'),w)
        with self.assertRaisesRegex(ValueError,'read address'):v.execute(code,v.ADDRESS,4,0,0,0,0)

    def test_wrong_callback_register_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='jsr')
        op,args,w=code[pc];code[pc]=(op,'r2',w)
        with self.assertRaisesRegex(ValueError,'callback target'):v.execute(code,v.ADDRESS,4,0x10207000,0,0,0)

if __name__=='__main__':unittest.main()
