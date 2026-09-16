# SPDX-License-Identifier: MIT
"""Decoded allocation-wrapper ABI/argument comparison; allocator bodies modeled."""
import json,subprocess,itertools
from build_gx8002_backup_heap_wrappers import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,delta,args,result,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r.update({f'r{i}':v for i,v in enumerate(args)});r['r14']=0x20070000;initial=r.copy();pc=entry;saved=None;events=[]
    for _ in range(30):
        op,text,width=code[pc];p=[v.strip() for v in text.split(',')]
        if op=='push':assert text=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert text=='r15';r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],events
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[1]]+r[p[2]])&0xffffffff
        elif op=='bsr':
            target=int(text,0)+delta;count=2 if target in (0x10009a44,0x10009c0c,0x10009ca4) else 1
            events.append((target,[r[f'r{i}'] for i in range(count)]))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError((op,text))
        pc+=width
    raise AssertionError('Execution bound')


def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x42850','--stop-address=0x42890',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-wrappers/wrappers.disassembly.txt').read_text())
    cases=0
    for entry,target,argc,zero in ((0x42850,0x42384,2,True),(0x4286c,0x423f8,1,False),(0x42874,0x4254c,2,False),(0x4287c,0x425e4,2,False),(0x42884,0x4256c,1,True)):
        for a,b,result,seed in itertools.product((0,1,512,0xffffffff),(0,4,0xffffffff),(0,0x20020000,0xffffffff),(0,0xa5a5a5a5)):
            args=[a,b];runtime=entry+0x10000000-0x38940
            expected_args=[0x2001bb80,0x2002cb80] if entry==0x42850 else args[:argc]
            expected=(0 if zero else result,[(target+0x10000000-0x38940,expected_args)])
            assert execute(old,entry,0x10000000-0x38940,args,result,seed)==execute(new,runtime,0,args,result,seed)==expected
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Allocator modeled; validates argument forwarding, normalized/preserved results and ABI only. Actual allocation semantics and hardware unqualified.']}
    (ROOT/'docs/research/gx8002-backup-heap-wrappers-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'])
