# SPDX-License-Identifier: MIT
"""Decoded backup GPIO direction/level register ordering and boundary behavior."""
import json, subprocess
from itertools import product
from build_gx8002_backup_gpio_output import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_gpio_output import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x40a94','--stop-address=0x40b2c',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-gpio-output/erase-linked.disassembly.txt').read_text())
    cases=0
    for level,pin,mode,first,second in product((False,True),(*range(65),0x7fffffff,0x80000000,0xffffffff),(0,1,2,3,0x80000000,0xffffffff),(0,0x55555555,0xaaaaaaaa,0xffffffff),(0,0x55555555,0xaaaaaaaa,0xffffffff)):
        memory={};word(memory,0xa0001000,first);word(memory,0xa0001004,first);word(memory,0xa0001008,second)
        expected_memory=memory.copy();expected=[];bit=1<<(pin&31)
        changes=[(0xa0001004,first|bit if mode else first&~bit)] if level else [(0xa0001000,first&~bit),(0xa0001008,second|bit)] if mode==0 else [(0xa0001008,second&~bit),(0xa0001000,first|bit)] if mode==1 else [(0xa0001008,second&~bit),(0xa0001000,first&~bit)] if mode==2 else []
        for address,value in changes:
            previous=sum(expected_memory[address+i]<<(8*i) for i in range(4))
            expected.append(('read','ld.w',address,previous))
            expected.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
            word(expected_memory,address,value)
        for code in (old,new):
            def helper(*args):raise AssertionError('unexpected helper')
            outcome,after,events=execute(code,0x100081b8 if level else 0x10008154,[pin,mode],memory,helper)
            assert outcome[:2]==('return',0) and after==expected_memory and events==expected,(level,pin,mode,first,second,outcome,events,expected)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Ordered modeled MMIO and ABI qualification; no physical hardware qualification.','Direction accepts modes 0/1/2; other values return zero without MMIO, matching stock.']}
    (ROOT/'docs/research/gx8002-backup-gpio-output-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
