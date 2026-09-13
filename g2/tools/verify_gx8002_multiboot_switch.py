# SPDX-License-Identifier: MIT
"""Qualify source multiboot marker publication and ordered cache/reboot calls."""
import json,re,subprocess,random
from itertools import product
from build_gx8002_multiboot_switch import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
ADDRESS=0x20033ffc
MAGIC=0xaabbccdd

def execute(code,entry,marker,result,mutation):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;pc=entry;condition=False;events=[]
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return marker,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('br','bt'):
            if op=='br' or condition:nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups()
            if r[base]+int(off,0)!=ADDRESS:raise ValueError('Marker address')
            if op=='ld.w':r[reg]=marker;events.append(('read',marker))
            else:marker=r[reg];events.append(('write',marker))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&0xffffffff
            if target==0x10206c24:
                events.append(('printf',r['r0'],marker))
                if mutation is not None:marker=mutation
            elif target==0x10025664:events.append(('clean',r['r0'],r['r1'],marker))
            elif target==0x102067b8:events.append(('reboot',marker))
            else:raise ValueError('Target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=result
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x1100c','--stop-address=0x1104c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-multiboot-switch/buffers.disassembly.txt').read_text());cases=0;rng=random.Random(91)
    values={0,1,0xffffffff,0x80000000,MAGIC,*[MAGIC^(1<<i) for i in range(32)],*[rng.getrandbits(32) for _ in range(256)]}
    for marker,result,mutation in product(sorted(values),(0,1,0x80000000,0xffffffff),(None,0,MAGIC,0xffffffff)):
        changed=0 if marker==MAGIC else MAGIC;message=0x1020b148 if marker==MAGIC else 0x1020b162
        expected=(changed,[('read',marker),('printf',message,marker),('write',changed),('clean',ADDRESS,16,changed),('reboot',changed)])
        for code,base in ((old,0),(new,0x101f6a74)):
            if execute(code,0x1100c+base,marker,result,mutation)!=expected:raise ValueError('Switch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Exact marker accesses, log-before-publication, sixteen-byte clean and reboot ordering; printf marker mutations overwritten as stock, helper clobbers and ABI checked. Cache/reboot modeled; no hardware invocation or qualification.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-multiboot-switch-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
