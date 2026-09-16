# SPDX-License-Identifier: MIT
"""Decoded backup board pin initialization call ordering and completion."""
import json, subprocess
from itertools import product
from build_gx8002_backup_board_pin_initialize import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_board_pin_initialize import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x412b8','--stop-address=0x41328',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-board-pin-initialize/erase-linked.disassembly.txt').read_text())
    cases=0
    for variant,errors,result in product(range(3),range(8192),(0,0xffffffff)):
        table=[((i*variant+2)&255,(i+variant)%3) for i in range(13)]
        memory={0x10012ecc+2*i+j:v for i,pair in enumerate(table) for j,v in enumerate(pair)}
        word(memory,0x200176d8,0xa5a5a5a5)
        pairs=[(0,1),*table[1:]]
        expected=[('init',0x10012ecc,13)]
        for i,(pin,function) in enumerate(pairs):
            if i:expected.extend([('read','ld.b',0x10012ecc+2*i,pin),('read','ld.b',0x10012ecd+2*i,function)])
            expected.append(('check',pin,function))
            if errors&(1<<i):expected.append(('printf',0x10012f38,pin))
            if function==int(pin!=2):expected.append(('direction',pin,0))
        expected.append(('setup',))
        expected.extend(('write_byte',0x200176d8+i,int(i==0)) for i in range(4))
        for code in (old,new):
            index=[0]
            def callback(target,args,state,events):
                if target==0x10008770:
                    assert args[:2]==[0x10012ecc,13];events.append(('init',*args[:2]));return result
                if target==0x100086dc:
                    assert args[:2]==list(pairs[index[0]])
                    value=0xffffffff if errors&(1<<index[0]) else 0;index[0]+=1
                    events.append(('check',*args[:2]));return value
                if target==0x10009934:events.append(('printf',*args[:2]));return result
                if target==0x10008154:events.append(('direction',*args[:2]));return result
                assert target==0x100088cc and index[0]==13
                events.append(('setup',));return result
            outcome,after,events=execute(code,0x10008978,[],memory,callback)
            assert outcome[0]=='return' and events==expected
            expected_memory=memory.copy();word(expected_memory,0x200176d8,1)
            assert after==expected_memory
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Pin helpers and printf modeled; setup returns in these cases.','Source pin-table and diagnostic storage remain separate unresolved dependencies.','Public void return value is not constrained; preserved-register ABI is checked. Candidate frame is four bytes larger than stock.']}
    (ROOT/'docs/research/gx8002-backup-board-pin-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
