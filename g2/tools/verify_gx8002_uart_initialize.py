# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,port,baud,clock,status,helpers,configure_hook=None,gate_hook=None,frequency_hook=None):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=port,r1=baud);initial=r.copy();saved=None;pc=entry;c=False;trace=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Initializer frame')
            saved={k:r[k] for k in ('r4','r5','r15')}
        elif op in ('pop','rts'):
            if op=='pop':r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Initializer ABI')
            return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='mvc':r[p[0]]=int(c)
        elif op=='incf':
            if not c:r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('cmphsi','cmpnei','cmplti'):
            a=r[p[0]];b=int(p[1],0);c=a>=b if op=='cmphsi' else a!=b if op=='cmpnei' else (a if a<0x80000000 else a-0x100000000)<b
        elif op in ('bt','bf','br'):
            if op=='br' or c==(op=='bt'):next_pc=int(args,0)
        elif op in ('addi','addu','subi','subu','lsli','rotli','mult','divu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            v=a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)) if op=='rotli' else a*b if op=='mult' else a//b
            r[p[0]]=v&0xffffffff
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();trace.append(('write',r[base]+int(off,0),r[reg]))
        elif op=='bsr':
            kind=helpers[int(args,0)];trace.append((kind,r['r0'],r['r1']) if kind=='gate' else (kind,r['r0']))
            result=clock if kind=='frequency' else status if kind=='configure' else 0
            if kind=='frequency' and frequency_hook is not None:result=frequency_hook(r['r0'])
            if kind=='gate' and gate_hook is not None:gate_hook(r['r0'],r['r1'])
            if kind=='configure' and configure_hook is not None:result=configure_hook(r['r0'],trace)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError(('Initializer opcode',op))
        pc=next_pc
    raise ValueError('Initializer bound')


def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xcabc','--stop-address=0xcb24',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-uart-initialize/initialize.disassembly.txt').read_text());cases=0
    clocks={0,1,0xffffffff}
    clocks.update(base+off for base in (0,1000000,24000000,4294000000) for off in (0,99,100,101,999899,999900,999901,999999) if base+off<=0xffffffff)
    for port,baud,clock,status in product((0,1,2,0xffffffff),(0,115200,0xffffffff),sorted(clocks),(0,7,0xffffffff)):
        rem=clock%1000000;rounded=clock-rem if rem<=100 else clock+1000000-rem if rem>=999900 else clock
        ptr=0x20026a94+port*128
        wanted=(0xffffffff,[]) if port>=2 else (status,[('gate',17+port,1),('frequency',16),('write',ptr+12,rounded&0xffffffff),('write',ptr+16,baud),('configure',ptr)])
        for code,entry,helpers in ((old,0xcabc,{0xffe2e60c:'gate',0xffe2e79c:'frequency',0xc954:'configure'}),(new,0x10203530,{0x10025080:'gate',0x10025210:'frequency',0x102033c8:'configure'})):
            if execute(code,entry,port,baud,clock,status,helpers)!=wanted:raise ValueError(('Initializer oracle',port,baud,clock,status))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded initializer with modeled gate/frequency/configuration calls. Boundary clock rounding, invalid ports and configuration result propagation checked; helper composition remains open.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Initializer cases:',r['cases'])
