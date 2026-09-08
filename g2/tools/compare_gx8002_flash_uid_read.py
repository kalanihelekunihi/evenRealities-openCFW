#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode UID read against independently ordered effects."""
import json,re,struct,subprocess
from build_gx8002_flash_uid_read import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
from model_gx8002_flash_uid_read import expected,MASK

def execute(code,pc,delta,offset,buffer,length,events,seed=0,frame=12,stop_at_chunk=False,summarize_receive=False,summary_word=0x12345678,summary_status=8):
    r={f'r{i}':(0x12340000+i+seed)&MASK for i in range(32)}
    r.update(r0=offset,r1=buffer,r2=length,r14=0x30001000);initial=r.copy();saved=None;local={};index=0;carry=False
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError(('effect mismatch',e,kind,address,value))
        return e[2]
    for _ in range(500000):
        if summarize_receive and pc==(0x10024176 if delta==0 else 0x16182):
            from verify_gx8002_uid_receive_step import check_structure
            check_structure(code,delta==0)
            end=r['r4' if delta==0 else 'r5'];distance=(end-r['r0'])&MASK
            if not distance or r['r3']!=0xa2000000 or not summary_status&8:
                raise ValueError('receive summary precondition')
            effect('receive-span',r['r0'],distance)
            r['r0']=end;r['r2']=summary_word
            if delta==0:r['r1']=summary_status
            carry=False;pc=0x1002416e if delta==0 else 0x1617a
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('frame')
            saved={i:r[f'r{i}'] for i in (4,5,15)};r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None or r['r14']!=initial['r14']-12:raise ValueError('return frame')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=12
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('return ABI/effects')
            return r['r0']
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andi','lsli','addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='andi' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='min.s32':
            signed=lambda v:v if v<0x80000000 else v-(1<<32)
            r[p[0]]=min(signed(r[p[1]]),signed(r[p[2]]))&MASK
            if stop_at_chunk:
                if index!=len(events):raise ValueError('chunk checkpoint effects')
                return r[p[0]]
        elif op=='rotli':
            a=r[p[1]];b=int(p[2],0);r[p[0]]=((a<<b)|(a>>(32-b)))&MASK
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
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
            if initial['r14']-frame<=address<initial['r14']-12:
                if op=='st.w':local[address]=r[reg]
                elif op=='ld.w':r[reg]=local[address]
                else:raise ValueError('local width')
            elif op in ('st.b','st.w'):effect('write',address,r[reg]&255 if op=='st.b' else r[reg])
            elif op=='ld.b':r[reg]=effect('byte-read',address)&255
            else:
                v=effect('read',address);r[reg]=v if op=='ld.w' else v&65535
                if op=='ld.hs' and r[reg]&32768:r[reg]|=0xffff0000
        elif op=='stbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);reg,base=m.groups()
            effect('byte-write',r[base],r[reg]&255);r[base]=(r[base]+1)&MASK
        elif op=='sexth':
            v=r[p[1]]&65535;r[p[0]]=v|0xffff0000 if v&32768 else v
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-frame:raise ValueError('call frame')
            target=int(args,0)+delta
            if target not in (0x1002364c,0x1002365c):raise ValueError('unknown helper')
            effect('call',target,[r[f'r{i}'] for i in range(3)] if target==0x10023b8c else [])
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xcafe0000+i+seed)&MASK
        else:raise ValueError('unknown write instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'uid-read-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x16118','--stop-address=0x161a4',str(w)],text=True))
    new=decode((out/'uid-read-linked.disassembly.txt').read_text());cases=0
    for requested in (*range(18),31,0x7fffffff):
     for manufacturer in (0,0x5e,0x85,0xff):
      for actual in (0x20029000,0x200264f0,0x20028004):
       for delay in (0,2):
        for seed in (0,0x1234):
         result,events=expected(0xfffffffe,requested,actual,manufacturer,delay)
         for code,entry,delta in ((old,0x16118,0x1000dfec),(new,0x10024104,0)):
            if execute(code,entry,delta,0xfffffffe,requested,actual,events,seed=seed)!=result:raise ValueError('UID result')
         cases+=1
    signed_checkpoints=0
    for requested in (0x80000000,0x80000001,0xffffff00,0xffffffff):
     for manufacturer in (0x5e,0x85):
      for seed in (0,0x1234):
        events=[['read',0x200264f0,0x20028000],['byte-read',0x20028006,manufacturer]]
        for code,entry,delta in ((old,0x16118,0x1000dfec),(new,0x10024104,0)):
            if execute(code,entry,delta,0xfffffffe,requested,0x20029000,events,seed=seed,stop_at_chunk=True)!=requested:
                raise ValueError('negative count selection')
        signed_checkpoints+=1
    summarized_cases=0
    for requested in (1,16,17,0x80000000,0x80000001,0xffffff00,0xffffffff):
     for seed in (0,0x1234):
      result,events=expected(0xfffffffe,requested,0x20029000,0x85,summarize_receive=True)
      for word,status in ((0,8),(0x12345678,0xffffffff),(0xffffffff,0x80000008)):
       for code,entry,delta in ((old,0x16118,0x1000dfec),(new,0x10024104,0)):
        if execute(code,entry,delta,0xfffffffe,requested,0x20029000,events,seed=seed,
                   summarize_receive=True,summary_word=word,summary_status=status)!=result:
            raise ValueError('summarized UID result')
      summarized_cases+=1
    report={'summarized_receive_cases':summarized_cases,'summary_postcondition_variants':3,'signed_count_checkpoints':signed_checkpoints,'build':evidence,'cases':cases,'frame_bytes':12,'source_admitted':False,
            'limits':['Finite decoded traces and summarized large transfers; receive-loop induction and rejection tests required for admission. No physical UID/controller qualification.']}
    (ROOT/'docs/research/gx8002-flash-uid-read-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
