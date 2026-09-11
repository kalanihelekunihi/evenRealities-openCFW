# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_initialize import build,programs,execute,expected,ADDRESS


class InitializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):build();cls.code=programs()[1]

    def test_flag_after_setup_return(self):
        table=[(p,int(p!=2)) for p in range(13)]
        self.assertEqual(execute(self.code,ADDRESS,table,0),expected(table,0,True))

    def test_no_flag_after_setup_nonreturn(self):
        table=[(p,int(p!=2)) for p in range(13)]
        self.assertEqual(execute(self.code,ADDRESS,table,8191,False),expected(table,8191,False))

    def test_non_gpio_function(self):
        table=[(p,3) for p in range(13)]
        self.assertEqual(execute(self.code,ADDRESS,table,0),expected(table,0,True))

    def test_setup_hook_overrides_assumed_return(self):
        table=[(p,int(p!=2)) for p in range(13)]
        calls=[]
        def stop():calls.append('setup');return False
        self.assertEqual(execute(self.code,ADDRESS,table,0,True,setup_hook=stop),expected(table,0,False))
        self.assertEqual(calls,['setup'])

    def test_checker_hook_drives_diagnostic(self):
        table=[(p,int(p!=2)) for p in range(13)]
        calls=[]
        def check(pin,function):
            calls.append((pin,function))
            return 0xffffffff if pin==2 else 0
        self.assertEqual(execute(self.code,ADDRESS,table,0,check_hook=check),expected(table,4,True))
        self.assertEqual(calls,table)

    def test_init_hook_arguments_and_ignored_error(self):
        table=[(p,int(p!=2)) for p in range(13)];calls=[]
        def initialize(pointer,size):calls.append((pointer,size));return 0xffffffff
        self.assertEqual(execute(self.code,ADDRESS,table,0,init_hook=initialize),expected(table,0,True))
        self.assertEqual(calls,[(0x1020ad30,13)])
