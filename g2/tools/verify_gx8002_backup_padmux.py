# SPDX-License-Identifier: MIT
"""Decoded backup pad-mux boundary checks and ordered MMIO behavior."""
import json, subprocess
from itertools import product
from build_gx8002_backup_padmux import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_padmux import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x4101c','--stop-address=0x410b0',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad','blz'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-padmux/erase-linked.disassembly.txt').read_text())
    cases=0
    for setter,pin,function,previous,readback in product((False,True),(*range(34),0x7fffffff,0x80000000,0xffffffff),(*range(17),255,256,0x7fffffff,0x80000000,0xffffffff),(0,0x55555555,0xffffffff),tuple(i*0x11111111 for i in range(16))):
        address=0xa0010090+4*(pin//8);shift=4*(pin%8)
        reads=[];expected=[];memory={};want=0xffffffff
        if setter and pin<=32:
            reads=[previous];expected.append(('read','ld.w',address,previous))
            value=(previous&~(15<<shift))|((function&15)<<shift)
            expected.extend(('write_byte',address+i,(value>>(8*i))&255) for i in range(4))
            if function<0x80000000:
                reads.append(readback);expected.append(('read','ld.w',address,readback))
                want=0 if (readback>>shift)&15==function else 0xffffffff
        elif not setter and pin<0x80000000 and function<0x80000000:
            if pin<=32:
                reads=[readback];expected=[('read','ld.w',address,readback)];value=(readback>>shift)&15
            else:value=255
            want=0 if value==function else 0xffffffff
        word(memory,address,previous)
        for code in (old,new):
            stream=iter(reads)
            def read(a):
                assert a==address
                return next(stream)
            def helper(*args):raise AssertionError('unexpected helper')
            outcome,after,events=execute(code,0x10008720 if setter else 0x100086dc,[pin,function],memory,helper,read)
            assert outcome[:2]==('return',want) and events==expected
            assert next(stream,None) is None
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['MMIO readback modeled independently of writes; no physical pad qualification.','Finite pin/function/register cases with preserved-register ABI and ordered MMIO checks.']}
    (ROOT/'docs/research/gx8002-backup-padmux-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
