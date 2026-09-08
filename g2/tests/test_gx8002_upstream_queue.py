# SPDX-License-Identifier: MIT
import ctypes
from collections import deque
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]

class Queue(ctypes.Structure):
    _fields_ = [('tail', ctypes.c_int), ('head', ctypes.c_int), ('buffer', ctypes.c_void_p),
                ('size', ctypes.c_int), ('member_size', ctypes.c_int)]

class UpstreamQueueTests(unittest.TestCase):
    def test_wraparound_full_empty_and_fifo(self):
        sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / 'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
            # Host-only placement shim; the target verifier uses the authenticated SDK header.
            (path / 'lvp_attr.h').write_text('#define DRAM0_STAGE2_SRAM_ATTR\n')
            library = path / 'queue.dylib'
            subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-I', str(path), '-I', str(sdk / 'include'),
                            str(sdk / 'lvp/common/lvp_queue.c'), '-o', str(library)], check=True)
            lib = ctypes.CDLL(str(library))
            lib.LvpQueueInit.argtypes = [ctypes.POINTER(Queue), ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
            for name in ('LvpQueuePut', 'LvpQueueGet'):
                getattr(lib, name).argtypes = [ctypes.POINTER(Queue), ctypes.c_void_p]
            for name in ('LvpQueueIsFull', 'LvpQueueIsEmpty', 'LvpQueueGetCapacity', 'LvpQueueGetDataNum'):
                getattr(lib, name).argtypes = [ctypes.POINTER(Queue)]
            rng = random.Random(0x10528)
            for member_size in (1, 3, 8):
                buffer = (ctypes.c_ubyte * (member_size * 8 + 2))()
                q = Queue()
                lib.LvpQueueInit(ctypes.byref(q), buffer, member_size * 8, member_size)
                expected = deque()
                self.assertEqual(lib.LvpQueueGetCapacity(ctypes.byref(q)), 8)
                for _ in range(4000):
                    item = (ctypes.c_ubyte * member_size)(*[rng.randrange(256) for _ in range(member_size)])
                    if rng.randrange(2):
                        full = len(expected) == 7
                        self.assertEqual(lib.LvpQueuePut(ctypes.byref(q), item), int(not full))
                        if not full:
                            expected.append(bytes(item))
                    else:
                        before = bytes(item)
                        self.assertEqual(lib.LvpQueueGet(ctypes.byref(q), item), int(bool(expected)))
                        self.assertEqual(bytes(item), expected.popleft() if expected else before)
                    self.assertEqual(lib.LvpQueueIsEmpty(ctypes.byref(q)), int(not expected))
                    self.assertEqual(lib.LvpQueueIsFull(ctypes.byref(q)), int(len(expected) == 7))
                    self.assertEqual(lib.LvpQueueGetDataNum(ctypes.byref(q)), len(expected))

if __name__ == '__main__':
    unittest.main()
