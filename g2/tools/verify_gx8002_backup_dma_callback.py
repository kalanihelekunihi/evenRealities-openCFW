# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_backup_dma_callback import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,channel,callback,private):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=channel,r1=callback,r2=private);initial=r.copy();writes=[]
    for _ in range(10):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='lrw':r[p[0]]=int(p[1],0)
        elif op in ('lsli','addu'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a+b)&0xffffffff
        elif op in ('st.w','str.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 2)\)',args)
            if not m:raise ValueError('Callback store syntax')
            reg,base,offset=m.groups();off=r[offset.split()[0]]<<2 if '<<' in offset else int(offset,0)
            writes.append(((r[base]+off)&0xffffffff,r[reg]))
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Callback ABI')
            return writes
        else:raise ValueError('Callback instruction '+op)
        pc+=width
    raise ValueError('Callback execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d5f8','--stop-address=0x3d60c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-callback/callback.disassembly.txt').read_text());cases=0
    for channel,callback,private in product((*range(16),0x3fffffff,0x40000000,0x7fffffff,0x80000000,0xffffffff),(0,0x102030e4,0xffffffff),(0,0x20026a94,0xffffffff)):
        base=(0x200174a8+(channel<<2))&0xffffffff;wanted=[(base,callback),((base+8)&0xffffffff,private)]
        if execute(old,0x3d5f8,channel,callback,private)!=wanted or execute(new,0x10004cb8,channel,callback,private)!=wanted:raise ValueError('Callback write contract')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Address arithmetic and ordered writes only. Extreme channels exercise arithmetic, not valid storage bounds. Slot arrays have not yet been reconstructed.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-dma-callback-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Callback cases:',result['decoded_cases'])
