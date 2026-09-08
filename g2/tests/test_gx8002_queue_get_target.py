# SPDX-License-Identifier: MIT
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_queue_get import execute

class QueueTargetTests(unittest.TestCase):
    def test_signed_division_truncates_toward_zero(self):
        code={0:('movi','r2, 0xfffffff9',4),4:('movi','r3, 3',2),
              6:('divs','r0, r2, r3',4),10:('rts','',2)}
        self.assertEqual(execute(code,{},0)[0],0xfffffffe)

    def test_indexed_byte_access_and_post_increment(self):
        code={0:('movi','r2, 2',2),2:('ldr.b','r3, (r0, r2 << 0)',4),
              6:('stbi.b','r3, (r1)',4),10:('rts','',2)}
        memory={0x1002:0x85,0x3000:0}
        _,trace=execute(code,memory,0)
        self.assertEqual(memory[0x3000],0x85)
        self.assertEqual(trace,[('read',0x1002,1),('write',0x3000,1)])
        with self.assertRaisesRegex(ValueError,'out-of-bounds'):
            execute(code,{},0)

    def test_post_increment_load_uses_old_address(self):
        code={0:('ldbi.b','r3, (r1)',4),4:('ldbi.b','r0, (r1)',4),8:('rts','',2)}
        result,trace=execute(code,{0x3000:0x91,0x3001:0x27},0)
        self.assertEqual(result,0x27)
        self.assertEqual(trace,[('read',0x3000,1),('read',0x3001,1)])

    def test_unknown_opcode_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('unknown','',2)},{},0)

if __name__=='__main__':unittest.main()
