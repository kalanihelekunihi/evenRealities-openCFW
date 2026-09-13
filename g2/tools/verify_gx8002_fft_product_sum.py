# SPDX-License-Identifier: MIT
"""Boundary checks and integer bounds for the Q15 product-sum optimization."""
import ctypes,itertools,json,subprocess
from build_gx8002_backup_radix4 import ROOT,sha

def verify():
    out=ROOT/'build/gx8002-backup-radix4';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4.c'
    harness='#include "'+str(source)+'"\nint32_t check_sum(int32_t a,int32_t b) { return sat_sum_products(a,b); }\n'
    (out/'product-sum.c').write_text(harness);path=out/'product-sum.dylib'
    subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(out/'product-sum.c'),'-o',str(path)],check=True)
    lib=ctypes.CDLL(str(path));fn=lib.check_sum;fn.argtypes=[ctypes.c_int32,ctypes.c_int32];fn.restype=ctypes.c_int32
    edge=(-32768,-32767,-1,0,1,32766,32767);cases=0
    for a,b,c,d in itertools.product(edge,repeat=4):
        expected=min(2147483647,a*b+c*d)
        assert fn(a*b,c*d)==expected;(cases:=cases+1)
    # A signed Q15 product's largest value requires both factors to be -32768.
    maximum=32768**2;next_maximum=32768*32767;minimum=-32768*32767
    assert maximum*2==2147483648
    assert maximum+next_maximum<=2147483647 and minimum*2>=-2147483648
    report={'source_sha256':sha(source.read_bytes()),'boundary_cases':cases,'product_bounds':{'maximum':maximum,'next_largest':next_maximum,'minimum':minimum},'unique_overflow_products':[maximum,maximum],'limits':['Integer bounds apply only to sums of two products of signed 16-bit factors. Helper is not a general saturating int32 addition.']}
    (ROOT/'docs/research/gx8002-fft-product-sum-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['boundary_cases'])
