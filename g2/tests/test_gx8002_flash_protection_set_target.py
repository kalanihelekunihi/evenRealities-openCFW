# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_protection_set import execute,oracle,execute_wrapper
class ProtectionSetTests(unittest.TestCase):
    def test_alias_clears_identifier_before_snapshot(self):
        result,events=oracle(0,0x85,0,0,[],2,0,123,0x20029004)
        self.assertEqual(result,0xffffffff)
        self.assertIn(['read4',0x20029004,0],events)
        self.assertFalse(any(e[:2]==['call',0x100236dc] for e in events))
    def test_alias_keeps_already_loaded_profile(self):
        result,events=oracle(0,0x85,0,0,[],2,0,123,0x20029010)
        self.assertEqual(result,0)
        self.assertIn(['read4',0x20029100,0x20029200],events)
    def test_wrapper_rejects_wrong_argument(self):
        code={0:('push','r15',2),2:('subi','r14, r14, 4',2),4:('mov','r1, r14',2),6:('bsr','0x100239a4',4)}
        with self.assertRaisesRegex(ValueError,'wrapper call'):
            execute_wrapper(code,0,0,17,0,0)
    def test_wrapper_requires_call(self):
        code={0:('push','r15',2),2:('pop','r15',2)}
        with self.assertRaisesRegex(ValueError,'wrapper return'):
            execute_wrapper(code,0,0,0,0,0)
    def test_unsorted_table_stops_at_first_larger(self):
        result,events=oracle(1,0x85,0xaa,0x55,[(1,255,2,255,2),(3,255,4,255,0)],2,0,0)
        self.assertEqual(result,0)
        self.assertFalse(any(e[0]=='read1' for e in events))
        command=next(e[2]['command'] for e in events if e[:2]==['call',0x100236dc])
        self.assertEqual(command,[0xaa,0x55])
    def test_failed_query_does_not_copy_output(self):
        result,events=oracle(0,0x85,0,0,[],2,0xffffffff,123)
        self.assertEqual(result,0xffffffff)
        self.assertEqual([e for e in events if e[0]=='write4'],[['write4',0x20028000,0]])
    def test_absent_profile_zero_request(self):
        self.assertEqual(oracle(0,0,0,0,[],0,0,0)[0],0)
        self.assertEqual(oracle(1,0,0,0,[],0,0,0)[0],0xffffffff)
    def test_uninitialized_stack_read(self):
        code={0:('subi','r14, r14, 40',2),2:('ld.w','r0, (r14, 0x0)',2)}
        with self.assertRaisesRegex(ValueError,'uninitialized stack'):
            execute(code,0,0,[],0,0,0)
    def test_invalid_command_arguments(self):
        with self.assertRaisesRegex(ValueError,'command arguments'):
            execute({0:('bsr','0x100236dc',4)},0,0,[['call',0x100236dc,{'command':[0,0],'return':0}]],0,0,0)
if __name__=='__main__':unittest.main()
