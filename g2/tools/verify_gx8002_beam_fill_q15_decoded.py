# SPDX-License-Identifier: MIT
"""Compare decoded stock packed fill with compiled pinned upstream C."""
import json,re,subprocess
from build_gx8002_beam_fill_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
def execute(code,entry,count,value):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=value,r1=0x1080,r2=count)
    initial=r.copy();memory=bytearray((i*73+19)&255 for i in range(2048));trace=[];pc=entry
    def access(address,size,write=None):
        assert 0x1000<=address and address+size<=0x1800 and address%size==0
        off=address-0x1000
        if write is None:
            value=int.from_bytes(memory[off:off+size],'little');trace.append(('read',address,size,value));return value
        value=write&((1<<(size*8))-1);trace.append(('write',address,size,value));memory[off:off+size]=value.to_bytes(size,'little')
    for _ in range(count*30+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='dup.16':
            lane=(r[p[1]]>>(16*int(p[2],0)))&65535
            r[p[0]]=lane|(lane<<16)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('subi','addi'):
            value=int(p[-1],0);r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(-value if op=='subi' else value))&0xffffffff
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(p[0],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('pldbi.d','ld.w','st.w','ldbi.h','stbi.h','stbi.w','st.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,offset=m.groups();address=r[base]+(int(offset,0) if offset else 0)
            if op=='pldbi.d':
                r[reg]=access(address,4);r['r'+str(int(reg[1:])+1)]=access(address+4,4);r[base]+=8
            else:
                size=2 if op.endswith('.h') else 4
                if op.startswith('ld'):r[reg]=access(address,size)
                else:access(address,size,r[reg])
                if 'bi.' in op:r[base]+=size
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return memory,trace
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47aec','--stop-address=0x47b14',str(path)],text=True))
    compiled=decode((ROOT/'build/gx8002-beam-fill-q15/fill.disassembly.txt').read_text());cases=0
    def bytes_written(trace):
        assert all(op=='write' for op,a,n,v in trace)
        return [(a+i,(v>>(8*i))&255) for op,a,n,v in trace for i in range(n)]
    for count in range(257):
        for value in (0,1,32767,32768,65535):
            before,bt=execute(original,0x47aec,count,value)
            after,at=execute(compiled,0x1000f1ac,count,value)
            assert before==after and bytes_written(bt)==bytes_written(at),(count,value)
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock and compiled C final memory and ordered byte-write expansion match at word-aligned RAM destinations.','Packed versus scalar transaction widths differ; no atomicity/MMIO/unaligned-access or complete uint32 count qualification. No integration yet.']}
    (ROOT/'docs/research/gx8002-beam-fill-q15-decoded.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
