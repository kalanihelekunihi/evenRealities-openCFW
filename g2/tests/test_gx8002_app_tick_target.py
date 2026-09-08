# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_app_tick import execute

class EventTickTargetTests(unittest.TestCase):
    def test_services_clobber_return_value_but_restore_saved_state(self):
        code={0:('push','r4, r15',2),2:('bsr','0x100',4),6:('movi','r0, 0',2),8:('pop','r4, r15',2)}
        self.assertEqual(execute(code,0,{256:'uart'},False,False,False,False,'none'),(0,[('uart',)]))

    def test_unknown_calls_and_bad_event_storage_rejected(self):
        args=(False,False,False,False,'none')
        with self.assertRaisesRegex(ValueError,'unknown direct call'):
            execute({0:('bsr','0x100',4)},0,{},*args)
        with self.assertRaisesRegex(ValueError,'outside write memory'):
            execute({0:('st.w','r0, (r1, 0x0)',2)},0,{},*args)

if __name__=='__main__':unittest.main()
