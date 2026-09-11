"""Exercise the GX8002 stage-2 libc leaf candidates; not target equivalence proof."""
import ctypes
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_stage2_libc import verify


class NativeContract(unittest.TestCase):
    def test_matches_libc_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / 'stage2_libc.dylib'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-O2', '-fno-builtin', '-shared', '-fPIC',
                            str(ROOT / 'components/shared/gx8002/runtime_gx8002_stage2_libc.c'),
                            '-o', str(library)], check=True)
            lib = ctypes.CDLL(str(library))
            lib.open_cfw_gx8002_stage2_strcmp.restype = ctypes.c_int
            lib.open_cfw_gx8002_stage2_strchr.restype = ctypes.c_void_p
            lib.open_cfw_gx8002_stage2_strlen.restype = ctypes.c_size_t
            lib.open_cfw_gx8002_stage2_strnlen.restype = ctypes.c_size_t

            def sign(n):
                return (n > 0) - (n < 0)

            pairs = [(b'', b''), (b'a', b'a'), (b'a', b'b'), (b'ab', b'a'),
                     (b'a', b'ab'), (bytes([1, 2, 3]), bytes([1, 2, 3])),
                     (bytes([0xff]), bytes([0x01]))]
            for a, b in pairs:
                got = lib.open_cfw_gx8002_stage2_strcmp(a, b)
                # Independent oracle: standard strcmp contract is sign-only.
                want = 0
                for x, y in zip(a, b):
                    if x != y:
                        want = 1 if x > y else -1
                        break
                else:
                    want = sign(len(a) - len(b))
                self.assertEqual(sign(got), want, (a, b, got))

            for s, c in ((b'hello', ord('l')), (b'hello', ord('z')), (b'', ord('a')), (b'abc', 0)):
                buf = ctypes.create_string_buffer(s)
                got = lib.open_cfw_gx8002_stage2_strchr(buf, c)
                index = s.find(bytes([c])) if c != 0 else len(s)
                if index < 0:
                    self.assertIsNone(got)
                else:
                    self.assertEqual(got, ctypes.addressof(buf) + index)

            for s in (b'', b'a', b'hello world'):
                self.assertEqual(lib.open_cfw_gx8002_stage2_strlen(s), len(s))
                for maxlen in (0, 1, len(s), len(s) + 5):
                    self.assertEqual(lib.open_cfw_gx8002_stage2_strnlen(s, maxlen), min(len(s), maxlen))


class DecodedExecutionContract(unittest.TestCase):
    def test_stock_and_candidate_agree_with_oracle(self):
        report = verify()
        self.assertTrue(report['source_admitted'])
        self.assertFalse(report['hardware_qualified'])
        self.assertEqual(len(report['functions']), 4)
        self.assertGreater(report['total_cases'], 10000)
        for kind in ('strcmp', 'strchr', 'strlen', 'strnlen'):
            self.assertGreater(report['cases'][kind], 0)


if __name__ == '__main__':
    unittest.main()
