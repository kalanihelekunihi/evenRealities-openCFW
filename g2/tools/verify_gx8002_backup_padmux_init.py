# SPDX-License-Identifier: MIT
"""Decoded backup pad-mux table search and setter call ordering."""
import json, subprocess
from itertools import product
from build_gx8002_backup_padmux_init import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_padmux_init import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x410b0','--stop-address=0x4111c',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad','blz'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-padmux-init/erase-linked.disassembly.txt').read_text())
    cases=0
    for variant,size,base,result in product(range(4),(0,1,13,32,33,0x80000000,0xffffffff),(0,0x20044000,0xffffffc0),(0,0xffffffff)):
        memory={};defaults=[((i+variant)%32,(i*variant)%16) for i in range(32)]
        overrides=[((i if variant%2==0 else i//2)%32,(i+variant)%16) for i in range(33)]
        for address,pairs in ((0x10012e74,defaults),(base,overrides)):
            for i,pair in enumerate(pairs):
                for j,v in enumerate(pair):memory[(address+2*i+j)&0xffffffff]=v
        valid=bool(base) and size<0x80000000;expected=[]
        if valid:
            for i in range(32):
                pin=0 if i==0 else defaults[i][0]
                if i:expected.append(('read','ld.b',0x10012e74+2*i,pin))
                matched=False
                for j,(candidate,function) in enumerate(overrides[:size]):
                    expected.append(('read','ld.b',(base+2*j)&0xffffffff,candidate))
                    if candidate==pin:
                        expected.append(('read','ld.b',(base+2*j+1)&0xffffffff,function));matched=True;break
                if not matched:
                    function=defaults[i][1];expected.append(('read','ld.b',0x10012e75+2*i,function))
                expected.append(('set',pin,function))
        for code in (old,new):
            def callback(target,args,state,events):
                assert target==0x10008720;events.append(('set',*args[:2]));return result
            outcome,after,events=execute(code,0x10008770,[base,size],memory,callback)
            assert outcome[:2]==('return',0 if valid else 0xffffffff)
            assert after==memory and events==expected,(variant,size,base,events,expected)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Setter modeled; finite override tables, including duplicates and wrapping pointers.','Defaults replaced by synthetic values to exercise first-pin constant and later loads. No hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-padmux-init-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
