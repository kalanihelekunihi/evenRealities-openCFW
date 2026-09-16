# SPDX-License-Identifier: MIT
"""Compare stock/source exceptional logf instruction paths without inventing FP policy."""
import json,random,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-log-exp-placed/math.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-log-exp-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x490a8','--stop-address=0x49300',str(wrapper)],text=True))
    rng=random.Random(94315)
    nonfinite=[(sign<<31)|0x7f800000|f for sign in (0,1) for f in [0,1,0x3fffff,0x400000,0x7fffff]+[rng.randrange(1<<23) for _ in range(100)]]
    negative=[0x80000000|(e<<23)|f for e in range(255) for f in (1,0x400000,0x7fffff)]
    negative += [0x80000000|rng.randrange(1,0x7f800000) for _ in range(1000)]
    cases=0
    for bits in nonfinite+negative+[0,0x80000000]:
        for intermediate,result_bits in ((0,0x7fc00001),(0x80000000,0xffa12345),(0x7fa54321,0x7fc98765)):
            expected=([('fdivs',0xcc000000,0)] if bits&0x7fffffff==0 else [('fsubs',bits,bits),('fdivs',intermediate,0)] if bits>>31 else [('fadds',bits,bits)])
            for code,entry in ((source,0x490a8-0x3b940+0x10003000),(old,0x490a8)):
                calls=[]
                def operation(op,*args):
                    calls.append((op,*args))
                    return intermediate if op=='fsubs' else result_bits
                actual=execute(code,entry,bytes(20),float_arguments=[bits],return_float=True,float_operation=operation)
                assert calls==expected and actual==result_bits,(hex(bits),calls,expected,hex(actual))
            cases+=1
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'paired_cases':cases,'nonfinite_inputs':len(nonfinite),'negative_finite_inputs':len(negative),'source_admitted':False,'limits':['Symbolic instruction-level operation and result propagation equivalence only. Negative NaNs follow the observed sign-first subtraction/division path; positive nonfinite values use addition. No assumptions about fused arithmetic, NaN quieting/payload, FP flags, traps or rounding modes; hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-logf-special-paths.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
