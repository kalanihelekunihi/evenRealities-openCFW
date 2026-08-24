#!/usr/bin/env python3
import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/fixtures/cordio_smpi_sc_act_host.c"
class CordioSmpiScActTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();out=Path(cls.tmp.name)/"lib.so"
        subprocess.run(["clang","-std=c11","-shared","-fPIC","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),"-o",str(out)],check=True)
        cls.lib=ctypes.CDLL(str(out))
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def check(self,name):
        f=getattr(self.lib,"open_cfw_test_smpi_sc_"+name);f.restype=ctypes.c_int;self.assertEqual(f(),0)
    def test_setup_and_send(self):self.check("setup_and_send")
    def test_jwnc_and_passkey(self):self.check("jwnc_and_passkey")
    def test_passkey_and_oob(self):self.check("passkey_and_oob_crypto")
    def test_dh_success_sets_key_ready(self):self.check("dh_success_key_ready")
    def test_dh_failure_retry(self):self.check("dh_failure_retry")
if __name__=="__main__":unittest.main()
