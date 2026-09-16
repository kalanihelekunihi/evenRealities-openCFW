#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Backup OTP erase instruction comparison; helpers modeled."""
import json,re,subprocess
from build_gx8002_backup_flash_erase import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,delta,offset,buffer,length,events,seed=0,frame=36,stop_at_chunk=False,instruction_limit=500000):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)}
    r.update(r0=offset,r1=buffer,r2=length,r14=0x30001000);initial=r.copy();saved=None;local={};index=0;carry=False
    event_iterator=iter(events);sentinel=object()
    def effect(kind,address,value=None):
        nonlocal index
        e=next(event_iterator,sentinel)
        if e is sentinel:raise ValueError('extra effect')
        index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError(('effect mismatch',e,kind,address,value))
        return e[2]
    for _ in range(instruction_limit):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            if saved is not None:raise ValueError('frame')
            regs=(*range(4,9),15) if delta else (*range(4,12),15,16)
            assert args==('r4-r8, r15' if delta else 'r4-r11, r15, r16')
            saved={i:r[f'r{i}'] for i in regs};r['r14']-=4*len(saved)
        elif op=='pop':
            if saved is None or r['r14']!=initial['r14']-4*len(saved):raise ValueError('return frame')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=4*len(saved)
            if next(event_iterator,sentinel) is not sentinel or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,16,17)):raise ValueError('return ABI/effects')
            return r['r0']
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andi','lsli','addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='andi' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)&MASK
        elif op=='max.u32':r[p[0]]=max(r[p[1]],r[p[2]])
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op in ('and','nor'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a&b if op=='and' else ~(a|b))&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='min.s32':
            signed=lambda v:v if v<0x80000000 else v-(1<<32)
            r[p[0]]=min(signed(r[p[1]]),signed(r[p[2]]))&MASK
            if stop_at_chunk:
                if next(event_iterator,sentinel) is not sentinel:raise ValueError('chunk checkpoint effects')
                return r[p[0]]
        elif op=='rotli':
            a=r[p[1]];b=int(p[2],0);r[p[0]]=((a<<b)|(a>>(32-b)))&MASK
        elif op=='bseti':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]]) | (1<<int(p[-1],0))
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='lsr':
            shift=r[p[-1]]&63;value=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=value>>shift if shift<32 else 0
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:n=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='cmpne':carry=r[p[0]]!=r[p[1]]
        elif op=='inct':
            if carry:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('cmpnei','cmphsi','cmphs'):
            b=r[p[1]] if op=='cmphs' else int(p[1],0)
            carry=r[p[0]]!=b if op=='cmpnei' else r[p[0]]>=b
        elif op in ('br','bt','bf','bez','bnez'):
            if op=='br' or op=='bt' and carry or op=='bf' and not carry or op=='bez' and not r[p[0]] or op=='bnez' and r[p[0]]:n=int(p[-1],0)
        elif op in ('ld.w','ld.h','ld.hs','ld.b','st.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if initial['r14']-frame<=address<initial['r14']-4*len(saved):
                if op=='st.w':local[address]=r[reg]
                elif op in ('ld.w','ld.b'):r[reg]=local[address]
                else:raise ValueError('local width')
            elif op in ('st.b','st.w'):effect('write',address,r[reg]&255 if op=='st.b' else r[reg])
            elif op=='ld.b':r[reg]=effect('byte-read',address)&255
            else:
                v=effect('read',address);r[reg]=v if op=='ld.w' else v&65535
                if op=='ld.hs' and r[reg]&32768:r[reg]|=0xffff0000
        elif op=='ldbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);reg,base=m.groups()
            r[reg]=effect('byte-read',r[base])&255;r[base]=(r[base]+1)&MASK
        elif op=='stbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);reg,base=m.groups()
            effect('byte-write',r[base],r[reg]&255);r[base]=(r[base]+1)&MASK
        elif op=='sexth':
            v=r[p[1]]&65535;r[p[0]]=v|0xffff0000 if v&32768 else v
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('call frame')
            target=int(args,0)+delta
            if target==0x10006cb0:
                effect('command',target,[r['r0'],r['r1'],r['r2']])
            elif delta:
                assert target==0x10006c30 and (r['r0'],r['r2'])==(5,1)
                assert initial['r14']-frame<=r['r1']<initial['r14']-24
                effect('ready',0x10007350,[])
                local[r['r1']]=0
            else:
                assert target==0x10007350
                effect('ready',target,[])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xcafe0000+i+seed)&MASK
        else:raise ValueError('unknown write instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    from itertools import product
    from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
    from build_transparent_image import Elf32
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3ff8c','--stop-address=0x400d0',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-erase/erase-linked.disassembly.txt').read_text());cases=0;large=0
    for address,length,size,widths in product((0,1,4095,4096,65535,65536,MASK),
            (0,1,4095,4096,65535,65536,65537,131072,MASK),(0,4096,65536,131072),((3,),(0,4,MASK))):
        events=[['read',0x20016d64,size]];want=0xffffffea
        if address<size:
            current=address&0xfffff000;remaining=(min((address+length)&MASK,size)-current)&MASK
            if remaining>131072:large+=1;continue
            want=0;epoch=0
            while remaining:
                chunk=65536 if current%65536==0 and remaining>=65536 else 4096
                w=widths[epoch%len(widths)];epoch+=1
                events.extend([['ready',0x10007350,[]],['command',0x10006cb0,[6,0,0]],['read',0x20016d68,w]])
                for i in range(1,5):
                    shift=((w-i)*8)&63
                    events.append(['write',0x20016d70+i,(current>>shift)&255 if shift<32 else 0])
                events.extend([['command',0x10006cb0,[0xd8 if chunk==65536 else 0x20,0x20016d71,3]],['ready',0x10007350,[]]])
                remaining=max(remaining,4096)-chunk;current=(current+chunk)&MASK
        for code,entry,delta,frame in ((old,0x3ff8c,0x10000000-0x38940,28),(new,0x1000764c,0,40)):
            assert execute(code,entry,delta,address,length,0,events,seed=0x1234,frame=frame)==want
        cases+=1
    report={'build':evidence,'cases':cases,'unqualified_large_range_inputs':large,'source_admitted':False,
            'limits':['Finite clamped ranges, block selection, width changes, ordered commands/encoding and ABI compared. Large wrapped-underflow ranges excluded explicitly; readiness/command helpers modeled and physical erases unqualified.']}
    (ROOT/'docs/research/gx8002-backup-erase-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
