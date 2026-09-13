# SPDX-License-Identifier: MIT
"""Qualify backup abort single base sample, six writes and deallocation."""
import re,json,subprocess
from itertools import product
from build_gx8002_backup_dma_abort import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,channel,base,status,clear_hook=None,deallocate_hook=None):
    registers={f'r{i}':0x87650000+i for i in range(32)}
    registers.update(r0=channel,r14=0x20070000);initial=registers.copy()
    pc=entry;saved=None;trace=[]
    for _ in range(30):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('Abort frame')
            saved=registers['r15'];registers['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('Abort restore')
            registers['r15']=saved;registers['r14']+=4
            if any(registers[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Abort ABI')
            return registers['r0'],trace
        elif op in ('mov','movi','lrw'):registers[p[0]]=registers[p[1]] if p[1] in registers else int(p[1],0)
        elif op in ('lsli','lsl'):
            a=registers[p[-2]] if len(p)==3 else registers[p[0]];b=registers[p[-1]] if p[-1] in registers else int(p[-1],0)
            registers[p[0]]=(a<<b)&0xffffffff
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('Abort memory operand')
            reg,pointer,offset=match.groups();address=(registers[pointer]+int(offset,0))&0xffffffff
            if op=='ld.w':
                if address!=0x2002d3e8:raise ValueError('Abort state read')
                registers[reg]=base;trace.append(('read',address,base))
            else:trace.append(('write',address,registers[reg]))
        elif op=='bsr':
            target=int(args,0)
            if target not in (0x3d500,0x10004bc0):raise ValueError('Abort helper target')
            kind='deallocate';hook=deallocate_hook
            trace.append((kind,registers['r0']))
            if hook is not None:hook(registers['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):registers[f'r{i}']=0xb0000000+i
            registers['r0']=status
        else:raise ValueError('Abort instruction '+op)
        pc+=width
    raise ValueError('Abort execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Abort stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d5c4','--stop-address=0x3d5f4',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-abort/abort.disassembly.txt').read_text());cases=0
    for channel,base,status in product(range(32),(0,0xa1000000,0xfffffe00),(0,1,0xffffffff)):
        wanted=(0,[('read',0x2002d3e8,base),('write',(base+0x3a0)&0xffffffff,(256<<channel)&0xffffffff),*[('write',(base+off)&0xffffffff,(1<<channel)&0xffffffff) for off in (0x338,0x340,0x348,0x350,0x358)],('deallocate',channel)])
        if execute(old,0x3d5c4,channel,base,status)!=wanted or execute(new,0x10004c84,channel,base,status)!=wanted:raise ValueError('Abort ordered contract')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
        'limits':['Defined shifts 0..31 checked; initialized hardware channels are 0/1. Helper effects modeled with caller-register clobbers; physical DMA cessation and concurrency unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-abort-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Abort cases:',r['decoded_cases'])
