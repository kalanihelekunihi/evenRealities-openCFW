# SPDX-License-Identifier: MIT
"""Compare decoded copy access traces, treating pldbi.d as two word reads."""
import json,re,subprocess
from build_gx8002_backup_copy_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,count,delta):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1080,r1=0x1080+delta,r2=count)
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
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('subi','addi'):
            value=int(p[-1],0);r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(-value if op=='subi' else value))&0xffffffff
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(p[0],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('pldbi.d','ld.w','st.w','ldbi.h','stbi.h','stbi.w'):
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
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47ac0','--stop-address=0x47aec',str(path)],text=True))
    compiled=decode((ROOT/'build/gx8002-backup-copy-q15/copy.disassembly.txt').read_text());cases=0
    for count in range(257):
        for delta in (*range(-32,33,4),1024):
            assert execute(original,0x47ac0,count,delta)==execute(compiled,0x1000f180,count,delta),(count,delta)
            cases+=1
    report={'build':evidence,'decoded_access_trace_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Full memory and ordered read/write values, widths and addresses compared over bounded counts and overlapping placements.','pldbi.d modeled as two word reads; hardware atomicity/bus transactions and full uint32 domain are not qualified. Placement remains pending.']}
    (ROOT/'docs/research/gx8002-backup-copy-q15-decoded.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_access_trace_cases'],'decoded access-trace cases')
