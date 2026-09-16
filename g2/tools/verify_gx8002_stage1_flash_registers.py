# SPDX-License-Identifier: MIT
"""Execute complete SPI register transfers with finite readiness sequences."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_flash_registers import build,ROOT,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,start,command,data,write,busy,seed):
    r={f'r{i}':(seed+i*0x12345)&MASK for i in range(32)};r.update(r0=command,r1=0x20002000,r2=len(data));saved=r.copy();mem=dict(enumerate(data,0x20002000));trace=[];pc=start;condition=False
    status=iter([1]*busy+[0]+sum(([0]*busy+[2 if write else 8] for _ in data),[])+[1]*busy+[0]);fifo=iter([1]*busy+[0]);received=iter(data)
    for _ in range(10000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='rotli':
            a=r[p[1]];n=int(p[2],0);r[p[0]]=((a<<n)|(a>>(32-n)))&MASK
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)*(1 if op=='addi' else -1))&MASK
        elif op=='addu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]])&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br','bez','bnez'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=(r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='rts':
            assert r['r0']==0 and all(r[f'r{i}']==saved[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert next(status,None) is None and next(fifo,None) is None
            if not write:assert next(received,None) is None
            return trace,bytes(mem[0x20002000+i] for i in range(len(data)))
        elif op in ('ld.w','st.w','ld.b','st.b','ldbi.b','stbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            reg,base,off=m.groups();a=r[base]+(int(off,0) if off else 0)
            if op.startswith('st'):
                v=r[reg] if op=='st.w' else r[reg]&255
                if a<0xa0000000:assert 0x20002000<=a<0x20002000+len(data);mem[a]=v
                trace.append(('write',a,v))
            else:
                if a==0xa2000028:v=next(status)
                elif a==(0xa2000020 if write else 0xa2000024):v=next(fifo)
                elif a==0xa2000060:assert not write;v=next(received)|0xa5a50000
                else:assert op!='ld.w';v=mem[a]
                r[reg]=v;trace.append(('read',a,v))
            if op in ('ldbi.b','stbi.b'):r[base]+=1
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify():
    evidence=build();out=ROOT/'build/gx8002-stage1-flash-registers';new=decode((out/'registers.disassembly.txt').read_text());pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');cases=0
    for write,off in ((False,0x39830),(True,0x398b0)):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={off:#x}',f'--stop-address={off+128:#x}',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
        for command,length,busy,seed in product((0,5,6,0x35,0x9f,255),(0,1,2,3,16,65),(0,1,3),(0x12345678,0x87654321)):
            data=bytes((i*37+command)&255 for i in range(length))
            a=execute(old,off,command,data,write,busy,seed);b=execute(new,off-0x38954+0x10000000,command,data,write,busy,seed);assert a==b,(write,command,length,busy)
            writes=[e for e in b[0] if e[0]=='write' and e[1]>=0xa0000000]
            expected=[(8,0),(0x4c,0),(0,0x407 if write else 0xc07),(4,length if write else (length-1)&MASK),(0x10,1),(0x18,length<<16 if write else 0),(0xf4,0),(8,1),(0x60,command)]
            if write:expected += [(0x60,v) for v in data]
            assert writes==[('write',0xa2000000+offset,value) for offset,value in expected]
            assert b[1]==data
            buffer_events=[e for e in b[0] if e[1]<0xa0000000]
            assert buffer_events==[('read' if write else 'write',0x20002000+i,v) for i,v in enumerate(data)]
            cases+=1
    report={'cases':cases,'build':evidence,'limits':['Complete helper decoded execution, independent command/configuration write oracle, buffer equality and ABI checks. Finite supplied ready/FIFO sequences; physical controller and nonterminating waits unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-flash-registers-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'register transfer cases passed')
