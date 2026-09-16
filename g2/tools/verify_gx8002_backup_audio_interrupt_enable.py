# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_backup_audio_interrupt_enable import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,source,left,right,seed):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=source,r1=left,r2=right)
    initial=r.copy();memory={0xa0a00000+off:seed^off for off in (0x100,0x104)};trace=[];pc=entry;condition=False
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Channel ABI')
            return r['r0'],trace,memory
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='nor':r[p[0]]=~(r[p[1]]|r[p[2]])&0xffffffff
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op=='andn':r[p[0]]&=~r[p[1]]
        elif op=='bnez':
            if r[p[0]]!=0:jump=int(p[1],0)
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Channel operand')
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&0xffffffff
            if address not in memory:raise ValueError('Channel MMIO address')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        else:raise ValueError('Channel instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Channel bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Channel stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3e5fc','--stop-address=0x3e628',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-audio-interrupt-enable/gain.disassembly.txt').read_text());cases=0
    for source,left,seed in product((0,0xffffffff,0xa5a5a5a5,*(1<<i for i in range(32))),(0,1,2,0x80000000,0xffffffff),(0,0xa5a5a5a5,0xffffffff)):
        right=0;memory={0xa0a00000+off:seed^off for off in (0x100,0x104)};trace=[]
        def clear():memory[0xa0a00104]=source;trace.append(('write',0xa0a00104,source))
        if left:clear()
        trace.append(('read',0xa0a00100,memory[0xa0a00100]))
        memory[0xa0a00100]=(memory[0xa0a00100]|source) if left else (memory[0xa0a00100]&~source)
        trace.append(('write',0xa0a00100,memory[0xa0a00100]))
        if not left:clear()
        wanted=(0,trace,memory)
        if execute(old,0x3e5fc,source,left,right,seed)!=wanted or execute(new,0x10005cbc,source,left,right,seed)!=wanted:raise ValueError('Channel selector oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Raw masks including every bit, nonzero enables, and opposite status-clear ordering checked. Physical interrupt delivery unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-audio-interrupt-enable-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Channel cases:',r['decoded_cases'])
