# SPDX-License-Identifier: MIT
import ctypes
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
import zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from generate_gx8002_crc_table import generate

class CrcSourceTests(unittest.TestCase):
    def test_alignment_lengths_and_seeded_incremental_crc(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);generate(p)
            libpath=p/'crc.dylib'
            subprocess.run(['cc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
                            str(ROOT/'components/shared/gx8002/runtime_gx8002_crc32.c'),
                            str(p/'crc_table.c'),'-o',str(libpath)],check=True)
            lib=ctypes.CDLL(str(libpath))
            for name in ('open_cfw_gx8002_crc32','open_cfw_gx8002_crc32_no_comp'):
                fn=getattr(lib,name);fn.argtypes=[ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint];fn.restype=ctypes.c_uint32
            rng=random.Random(0x12d80)
            for alignment in range(4):
                for size in range(513):
                    data=bytes(rng.randrange(256) for _ in range(size))
                    storage=(ctypes.c_ubyte*(size+8))()
                    address=ctypes.addressof(storage)+alignment
                    ctypes.memmove(address,data,size)
                    before=bytes(storage);seed=rng.getrandbits(32)
                    expected=zlib.crc32(data,seed)
                    self.assertEqual(lib.open_cfw_gx8002_crc32(seed,address,size),expected)
                    self.assertEqual(lib.open_cfw_gx8002_crc32_no_comp(seed^0xffffffff,address,size)^0xffffffff,expected)
                    cut=size//2
                    first=lib.open_cfw_gx8002_crc32(seed,address,cut)
                    self.assertEqual(lib.open_cfw_gx8002_crc32(first,address+cut,size-cut),expected)
                    self.assertEqual(bytes(storage),before)

if __name__=='__main__':unittest.main()
