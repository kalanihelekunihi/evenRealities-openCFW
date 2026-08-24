#!/usr/bin/env python3
import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/fixtures/cordio_smpr_sc_act_host.c"
class CordioSmprScActTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();out=Path(cls.tmp.name)/"lib.so"
        subprocess.run(["clang","-std=c11","-shared","-fPIC","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),"-o",str(out)],check=True)
        cls.lib=ctypes.CDLL(str(out))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def check(self,name):
        f=getattr(self.lib,"open_cfw_test_smpr_sc_"+name);f.restype=ctypes.c_int;self.assertEqual(f(),0)
    def test_store_and_setup(self):self.check("store_and_setup")
    def test_jwnc_and_passkey(self):self.check("jwnc_and_passkey")
    def test_passkey_failure_and_oob(self):self.check("passkey_failure_and_oob")
    def test_dh_success_sets_key_ready(self):self.check("dh_success_key_ready")
    def test_dh_failure_retry(self):self.check("dh_failure_retry")
    def test_dh_store_wait_calculate(self):self.check("dh_store_wait_calculate")
if __name__=="__main__":unittest.main()
