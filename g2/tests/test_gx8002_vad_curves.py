# SPDX-License-Identifier: MIT
import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_vad_curves import SOURCE,execute


class CurveHostTests(unittest.TestCase):
    def test_boundaries_and_independent_hardware_readbacks(self):
        fixture_text='''#include <stdint.h>
uint32_t reads[2];
uint32_t events[12];
unsigned read_count, event_count;
uint32_t open_cfw_gx8002_vad_read(unsigned index) {
 uint32_t value = reads[read_count++];
 events[event_count++]=0; events[event_count++]=index; events[event_count++]=value;
 return value;
}
void open_cfw_gx8002_vad_write(unsigned index,uint32_t value) {
 events[event_count++]=1; events[event_count++]=index; events[event_count++]=value;
}
'''
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);fixture=root/'fixture.c';library=root/'curves.so'
            fixture.write_text(fixture_text)
            subprocess.run(['/usr/bin/clang','-O2','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',
                            '-DOPEN_CFW_GX8002_VAD_HOST_TEST',str(SOURCE),str(fixture),'-o',str(library)],check=True,capture_output=True)
            lib=ctypes.CDLL(str(library))
            reads=(ctypes.c_uint32*2).in_dll(lib,'reads');events=(ctypes.c_uint32*12).in_dll(lib,'events')
            read_count=ctypes.c_uint.in_dll(lib,'read_count');event_count=ctypes.c_uint.in_dll(lib,'event_count')
            boundaries=(0,1,3072,3073,4096,4097,5120,5121,7680,7681,8192,8193,17920,17921,32768,60415,60416,65535)
            rng=random.Random(0x184)
            cases=[(a,b) for a in boundaries for b in boundaries]
            cases += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(2048)]
            for curve in range(1,6):
                fn=getattr(lib,f'gx_audio_in_set_fftvad_curve_{curve}')
                argtype=ctypes.c_int16 if curve==3 else ctypes.c_uint16
                fn.argtypes=[argtype]*(1 if curve==5 else 2);fn.restype=ctypes.c_int
                for a,b in cases:
                    signed_b=b if b<32768 else b-65536
                    valid={1:a<=3072 and b<=17920,2:a<=3072 and b<=7680,
                           3:a<=4096 and -5120<=signed_b<=5120,4:a<=5120 and b<=5120,5:a<=8192}[curve]
                    old,new=rng.getrandbits(32),rng.getrandbits(32)
                    reads[:]=[old,new];read_count.value=event_count.value=0
                    result=fn(a) if curve==5 else fn(a,b)
                    self.assertEqual(result,0 if valid else -1,(curve,a,b))
                    expected=[]
                    index=(0x180+curve*4)//4
                    if valid:
                        expected=[0,index,old,1,index,(old&0xffff0000)|a]
                        if curve!=5: expected += [0,index,new,1,index,(new&0xffff)|(b<<16)]
                    self.assertEqual(list(events)[:event_count.value],expected,(curve,a,b))
                    self.assertEqual(read_count.value,0 if not valid else (1 if curve==5 else 2))


class TargetInterpreterTests(unittest.TestCase):
    def test_unknown_opcode_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:(2,'jsr','r0')},0,0,(0,0))

    def test_unsigned_comparison_and_signed_return_bits(self):
        code={0:(4,'cmphsi','r0, 3073'),4:(2,'bt','0x8'),6:(2,'rts',''),
              8:(2,'movi','r0, 0'),10:(2,'subi','r0, 1'),12:(2,'rts','')}
        self.assertEqual(execute(code,3073,0,(0,0)),(0xffffffff,[]))


if __name__=='__main__':unittest.main()
