# SPDX-License-Identifier: MIT
"""Decoded UART output against stock and an ordered MMIO oracle."""
import itertools,json,re,subprocess
from build_gx8002_backup_uart_putc import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,port,character,status,seed):
    r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=port;r['r1']=character;initial=r.copy();pc=entry;condition=False;events=[];reads=iter(status);descriptor=(0x20016b88+(port<<7))&MASK;base=0xa0000000
    for _ in range(200):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));assert next(reads,None) is None
            return events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[1]]+r[p[2]] if len(p)==3 else r[p[0]]+r[p[1]])&MASK
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0) if len(p)==3 else r[p[0]]+int(p[1],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[0],0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,b,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[b]+int(off,0))&MASK
            if op=='ld.w':
                if a==descriptor:value=base
                else:assert a==base+20;value=next(reads)
                r[reg]=value;events.append(('read',a,value))
            else:assert a==base;events.append(('write',a,r[reg]))
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x3cee0','--stop-address=0x3cf18',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-backup-uart-putc/putc.disassembly.txt').read_text());cases=0
    for port,char,delay,ready,seed in itertools.product((0,1,2,MASK),list(range(256))+[266,MASK],(0,1,5),(32,0xffffffff),(0,0xa5a5a5a5)):
        phase=[0x80]*delay+[ready];status=phase*(2 if char==10 else 1)
        expected=[('read',(0x20016b88+(port<<7))&MASK,0xa0000000)]
        for value in ([13,10] if char==10 else [char&255]):expected += [('read',0xa0000014,v) for v in phase]+[('write',0xa0000000,value)]
        assert execute(old,0x3cee0,port,char,status,seed)==execute(new,0x100045a0,port,char,status,seed)==expected
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Exact ordered descriptor/MMIO reads and writes, ready polling, CRLF and low-byte output, preserved registers'],'limits':['Finite modeled ready delays; synthetic port indices do not establish valid hardware descriptors. Integration and hardware execution pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-uart-putc-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
