#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Backup OTP read decoder; qualification currently covers rejection and first chunk."""
import json,re,subprocess
from build_gx8002_backup_otp_write import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,delta,offset,buffer,length,events,seed=0,frame=36,stop_at_chunk=False):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)}
    r.update(r0=offset,r1=buffer,r2=length,r14=0x30001000);initial=r.copy();saved=None;local={};index=0;carry=False
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError(('effect mismatch',e,kind,address,value))
        return e[2]
    for _ in range(500000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            if saved is not None:raise ValueError('frame')
            regs=(*range(4,12),15,16) if delta else (*range(4,11),15)
            assert args==('r4-r11, r15, r16' if delta else 'r4-r10, r15')
            saved={i:r[f'r{i}'] for i in regs};r['r14']-=4*len(saved)
        elif op=='pop':
            if saved is None or r['r14']!=initial['r14']-4*len(saved):raise ValueError('return frame')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=4*len(saved)
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,16,17)):raise ValueError('return ABI/effects')
            return r['r0']
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andi','lsli','addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='andi' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='min.s32':
            signed=lambda v:v if v<0x80000000 else v-(1<<32)
            r[p[0]]=min(signed(r[p[1]]),signed(r[p[2]]))&MASK
            if stop_at_chunk:
                if index!=len(events):raise ValueError('chunk checkpoint effects')
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
            if target in (0x10006cb0,0x10007790):
                effect('call',target,[r['r0'],r['r1'],r['r2']])
            elif delta:
                assert target==0x10006c30 and (r['r0'],r['r2'])==(5,1)
                effect('ready',0x10007350,[])
                local[r['r1']]=0
            else:
                assert target==0x10007350
                effect('ready',target,[])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xcafe0000+i+seed)&MASK
        else:raise ValueError('unknown write instruction '+op)
        pc=n
    raise ValueError('execution bound')
def expected(offset,buffer,length,size,manufacturer,widths):
    events=[['read',0x20016d6c,0x20028000],['read',0x20028014,0x20028100],['read',0x20028110,7]]
    if not length:return MASK,events
    events.append(['read',0x20028108,size])
    if (offset+length)&MASK>size:return MASK,events
    base=0xfffff000;stride=0x1000
    events.extend([['read',0x20028100,base],['read',0x20028104,stride],['read',0x20028006,manufacturer]])
    if manufacturer not in (0x5e,0x85):return MASK,events
    address=(base+offset+7*stride)&MASK;epoch=0
    def width():
        nonlocal epoch
        value=widths[epoch%len(widths)];epoch+=1
        events.append(['read',0x20016d68,value]);return value
    def encode(address,w,indices):
        for i in indices:
            shift=((w-i)*8)&63
            events.append(['write',0x20016d70+i,(address>>shift)&255 if shift<32 else 0])
    def ready():events.append(['ready',0x10007350,[]])
    def enable():events.append(['call',0x10006cb0,[6,0,0]])
    def transmit(w,done,chunk):events.append(['call',0x10007790,[(w+1)&MASK,(buffer+done)&MASK,chunk]])
    ready();enable();events.append(['write',0x20016d70,0x42])
    w=width();encode(address,w,(1,2,4,3));page_offset=address&255
    if (length+page_offset)&MASK<=256:
        transmit(w,0,length)
    else:
        done=256-page_offset;transmit(w,0,done)
        assert length<65536,'unbounded model input'
        while done<length:
            encode((address+done)&MASK,width(),(1,2,3,4));ready();enable()
            chunk=min(length-done,256);transmit(width(),done,chunk);done+=chunk
    ready();return length,events


def verify():
    from itertools import product
    from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
    from build_transparent_image import Elf32
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x401c4','--stop-address=0x40328',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-otp-write/otp-write-linked.disassembly.txt').read_text());cases=0
    inputs=list(product((0,1,127,255,256,MASK),(0,1,2,255,256,257,511,512,513),(0,512,MASK),(0,0x5e,0x85,0xffff),((3,),(0,4,MASK,3))))
    inputs.extend((offset,MASK,MASK,0x85,(3,)) for offset in (1,127,255))
    for offset,length,size,manufacturer,widths in inputs:
        result,events=expected(offset,0xfffffffe,length,size,manufacturer,widths)
        for code,entry,delta,frame in ((old,0x401c4,0x10000000-0x38940,44),(new,0x10007884,0,32)):
            assert execute(code,entry,delta,offset,0xfffffffe,length,events,seed=0x1234,frame=frame)==result
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Ordered descriptor reads, byte encoding, width reloads, page splits, helper arguments and saved ABI compared. Includes wrapped single-call high lengths without executing their huge transfers. Ready, command and transmit effects modeled; actual composed transfers and physical writes remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-otp-write-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])
