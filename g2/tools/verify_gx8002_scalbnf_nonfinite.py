# SPDX-License-Identifier: MIT
"""Check that stock/source nonfinite paths delegate exactly the same FP addition."""
import json,subprocess,random
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute

def verify():
    path=ROOT/'build/gx8002-scalbnf-placed/scale.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-scalbnf-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x49ad4','--stop-address=0x49bd8',str(wrapper)],text=True))
    rng=random.Random(3267);payloads=[0,1,0x3fffff,0x400000,0x7fffff]+[rng.randrange(1<<23) for _ in range(100)]
    cases=0
    for sign in (0,1):
        for payload in payloads:
            bits=(sign<<31)|0x7f800000|payload
            for n in (-2147483648,-25,0,25,2147483647):
                for symbolic_result in (0x7fc00001,0xffa12345):
                    for code,entry in ((source,0x49ad4-0x3b940+0x10003000),(old,0x49ad4)):
                        calls=[]
                        def operation(op,a,b):
                            calls.append((op,a,b));return symbolic_result
                        result=execute(code,entry,bytes(20),arguments=[n&0xffffffff],float_arguments=[bits],return_float=True,float_operation=operation)
                        assert calls==[('fadds',bits,bits)] and result==symbolic_result
                    cases+=1
    result={'elf_sha256':sha(data),'paired_cases':cases,'source_admitted':False,'limits':['Symbolic FP callback proves same x+x operation and unchanged result propagation for sampled nonfinite inputs. It does not model NaN policy, status flags, exception dispatch or hardware rounding.']}
    (ROOT/'docs/research/gx8002-scalbnf-nonfinite-paths.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify())
