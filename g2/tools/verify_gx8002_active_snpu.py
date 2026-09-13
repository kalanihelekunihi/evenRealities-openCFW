# SPDX-License-Identifier: MIT
"""Decoded active SNPU callback record ABI and ignored queue-return checks."""
import json,re,subprocess,itertools
from build_gx8002_active_snpu_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,module,state,private,result,seed,queue_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=module,r1=state,r2=private,r14=0x20070000);initial=r.copy();saved=None;memory={};events=[];pc=entry
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':assert args=='r15' and saved is None;saved=r['r15'];r['r14']-=4
        elif op in ('addi','subi'):
            assert p==['r14','r14','8'];r['r14']+=8 if op=='addi' else -8
        elif op in ('movi','lrw','mov'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='st.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);assert address in (0x2006fff4,0x2006fff8);memory[address]=r[reg]
        elif op=='bsr':
            assert int(args,0)+(0x1000dfec if entry==0x18354 else 0)==0x100261b8
            assert r['r0']==0x2002e6ec and r['r1']==r['r14']==0x2006fff4
            record=(memory[r['r1']],memory[r['r1']+4]);events.append(('put',r['r0'],record))
            value=result if queue_hook is None else queue_hook(r['r0'],record)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value&MASK
        elif op=='pop':
            assert args=='r15' and r['r14']==0x2006fffc;r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],events
        else:raise ValueError((op,args))
        pc+=width
    raise ValueError('callback bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';path=out/'padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA and elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x18354','--stop-address=0x1836c',str(path)],text=True));new=decode((out/'active-snpu.disassembly.txt').read_text());cases=0
    for args in itertools.product((0,256,MASK),(0,1,MASK),(0,0x20030000,MASK),(0,1,MASK),(0,91)):
        expected=(0,[('put',0x2002e6ec,(args[0],args[2]))])
        assert execute(old,0x18354,*args)==execute(new,0x10026340,*args)==expected;cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stack record, call target, ignored state and queue return, and callee ABI checked. Queue body modeled; source literal placement exceeds original envelope and remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-active-snpu-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
