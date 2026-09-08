"""Exercise the recovered ordinary-RAM contract; not target equivalence proof."""
import ctypes
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_memcpy_source import execute


class CopyContract(unittest.TestCase):
    def test_alignment_lengths_and_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            library = Path(directory) / 'copy.dylib'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-O2', '-fno-builtin', '-shared', '-fPIC',
                            str(ROOT / 'components/shared/gx8002/runtime_gx8002_memcpy.c'),
                            '-o', str(library)], check=True)
            copy = ctypes.CDLL(str(library)).open_cfw_gx8002_memcpy
            copy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            copy.restype = ctypes.c_void_p
            for source_alignment in range(4):
                for destination_alignment in range(4):
                    for length in range(258):
                        original = bytes((i * 73 + 19) % 256 for i in range(280))
                        source = (ctypes.c_ubyte * 280).from_buffer_copy(original)
                        destination = (ctypes.c_ubyte * 280)(*([0xa5] * 280))
                        start = 8 + destination_alignment
                        pointer = ctypes.addressof(destination) + start
                        self.assertEqual(copy(pointer, ctypes.addressof(source) + source_alignment,
                                              length), pointer)
                        expected = bytearray([0xa5] * 280)
                        expected[start:start + length] = original[source_alignment:source_alignment + length]
                        self.assertEqual(bytes(destination), bytes(expected))
                        self.assertEqual(bytes(source), original)


class TargetInterpreter(unittest.TestCase):
    def test_post_increment_and_decrement_branch(self):
        code = {0: ('stbi.b', 'r1, (r0)', 4),
                4: ('bnezad', 'r2, 0x0', 4), 8: ('rts', '', 2)}
        memory = {}
        result, trace = execute(code, memory, 0x3000, 0x1042, 2)
        self.assertEqual(result, 0x3002)
        self.assertEqual(memory, {0x3000: 0x42, 0x3001: 0x42})
        self.assertEqual(trace, [('write', 0x3000), ('write', 0x3001)])

    def test_word_access_and_unsigned_comparison(self):
        code = {0: ('cmplti', 'r2, 4', 2), 2: ('bt', '0xc', 2),
                4: ('ld.w', 'r3, (r1, 0x0)', 4),
                8: ('st.w', 'r3, (r0, 0x0)', 4), 12: ('rts', '', 2)}
        memory = {0x1000+i: i+1 for i in range(4)}
        result, trace = execute(code, memory, 0x3000, 0x1000, 4)
        self.assertEqual(result, 0x3000)
        self.assertEqual([memory[0x3000+i] for i in range(4)], [1, 2, 3, 4])
        self.assertEqual(len(trace), 8)
        _, trace = execute(code, {}, 0x3000, 0x1000, 3)
        self.assertEqual(trace, [])
        with self.assertRaisesRegex(ValueError, 'unaligned word access'):
            execute(code, {}, 0x3000, 0x1001, 4)

    def test_unknown_opcode_and_out_of_bounds_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'unsupported instruction'):
            execute({0: ('trap', '', 2)}, {}, 0x3000, 0x1000, 0)
        with self.assertRaisesRegex(ValueError, 'read outside source'):
            execute({0: ('ld.b', 'r3, (r1, 0x0)', 2)}, {}, 0x3000, 0x1000, 0)


if __name__ == '__main__':
    unittest.main()
