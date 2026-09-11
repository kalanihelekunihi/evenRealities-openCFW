# SPDX-License-Identifier: MIT
import json,subprocess
from build_gx8002_dma_bus_address import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,address):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=address;initial=r.copy();condition=False
    for _ in range(10):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','lsli'):
            a=r[p[1]];b=r[p[2]] if p[2] in r else int(p[2],0)
            r[p[0]]=(a+b if op=='addu' else a<<b)&0xffffffff
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='bf':
            if not condition:jump=int(args,0)
        elif op=='zext':
            high,low=int(p[2],0),int(p[3],0);r[p[0]]=(r[p[1]]>>low)&((1<<(high-low+1))-1)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Bus address ABI')
            return r['r0']
        else:raise ValueError('Bus address instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Bus address execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd1ec','--stop-address=0xd200',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-bus-address/bus_address.disassembly.txt').read_text());cases=0
    values={((base+delta)&0xffffffff) for base in (0,0x10000000,0x20000000,0x30000000,0x80000000,0xffffffff) for delta in range(-32,33)}
    values.update((high<<16)|low for high in range(65536) for low in (0,0xffff))
    for address in sorted(values):
        wanted=address%0x10000000 if 0x10000000<=address<0x30000000 else address
        if execute(old,0xd1ec,address)!=wanted or execute(new,0x10203c60,address)!=wanted:raise ValueError('Bus address mapping')
        cases+=1
    row=candidate['functions'][0]
    if row['compiled_sha256']!=row['stock_sha256']:raise ValueError('Bus address exact instruction identity')
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite mapping corpus covers both ends of every 64KiB block and dense alias boundaries; physical bus addressability not proved.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-bus-address-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Bus address cases:',result['decoded_cases'])
