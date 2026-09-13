# SPDX-License-Identifier: MIT
"""Compare decoded C-SKY fill store traces with the stock DSP helper."""
import json,re,subprocess
from build_gx8002_backup_fill_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,value,count):
    regs={f'r{i}':0x76540000+i for i in range(32)}
    regs.update(r0=value,r1=0x1000,r2=count);initial=regs.copy()
    pc=entry;condition=False;trace=[]
    for _ in range(20*count+100):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='lsri':regs[p[0]]=regs[p[1]]>>int(p[2],0)
        elif op=='lsli':regs[p[0]]=(regs[p[1]]<<int(p[2],0))&MASK
        elif op=='zexth':regs[p[0]]=regs[p[1]]&65535
        elif op=='dup.16':regs[p[0]]=(regs[p[1]]&65535)*0x10001
        elif op=='andi':regs[p[0]]=regs[p[1]]&int(p[2],0)
        elif op=='mov':regs[p[0]]=regs[p[1]]
        elif op=='addu':regs[p[0]]=(regs[p[0] if len(p)==2 else p[1]]+regs[p[-1]])&MASK
        elif op=='addi':regs[p[0]]=(regs[p[0] if len(p)==2 else p[1]]+int(p[-1],0))&MASK
        elif op=='cmpne':condition=regs[p[0]]!=regs[p[1]]
        elif op=='bez':
            if regs[p[0]]==0:nxt=int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(p[0],0)
        elif op in ('bnezad','bloop'):
            regs[p[0]]=(regs[p[0]]-1)&MASK
            if regs[p[0]]:nxt=int(p[1],0)
        elif op in ('st.w','stbi.w','stbi.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            src,base,offset=m.groups();size=2 if op.endswith('.h') else 4
            address=regs[base]+(int(offset,0) if offset else 0)
            assert 0x1000<=address and address+size<=0x1000+count*2
            assert address%size==0
            trace.append((address,size,regs[src]&((1<<(size*8))-1)))
            if op.startswith('stbi'):regs[base]=(regs[base]+size)&MASK
        elif op=='rts':
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return trace
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('Instruction bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47aec','--stop-address=0x47b14',str(wrapper)],text=True))
    compiled=decode((ROOT/'build/gx8002-backup-fill-q15/fill.disassembly.txt').read_text())
    cases=0
    for count in range(1025):
        for value in (0,1,0x7fff,0x8000,0xffff,0x12345678,0x80000000,0xffffffff):
            expected=execute(original,0x47aec,value,count)
            actual=execute(compiled,0x1000f1ac,value,count)
            assert actual==expected,(count,value)
            assert sum(size for _,size,_ in actual)==count*2
            cases+=1
    result={'build':evidence,'decoded_trace_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Counts 0..1024, eight values, exact store address/width/value/order and callee-saved register comparison.','Instruction model, not hardware or full uint32 count-domain proof. Alignment contract inherited from stock. Candidate exceeds stock envelope.']}
    (ROOT/'docs/research/gx8002-backup-fill-q15-decoded.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['decoded_trace_cases'],'decoded store-trace cases')
