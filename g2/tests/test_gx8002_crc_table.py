# SPDX-License-Identifier: MIT
import random
import sys
import unittest
import zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from generate_gx8002_crc_table import table_values

class TableTests(unittest.TestCase):
    def test_generated_recurrence_against_zlib(self):
        table=table_values()
        self.assertEqual(len(table),256)
        def update(seed,data):
            crc=seed^0xffffffff
            for byte in data:crc=table[(crc^byte)&255]^(crc>>8)
            return crc^0xffffffff
        self.assertEqual(update(0,b'123456789'),0xcbf43926)
        rng=random.Random(0xedb88320)
        for size in range(1025):
            data=bytes(rng.randrange(256) for _ in range(size))
            seed=rng.getrandbits(32)
            expected=zlib.crc32(data,seed)
            self.assertEqual(update(seed,data),expected)
            split=size//2
            self.assertEqual(update(update(seed,data[:split]),data[split:]),expected)

if __name__=='__main__':unittest.main()
