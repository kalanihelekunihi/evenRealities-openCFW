#!/usr/bin/env python3
"""Ordered decoded protection-query comparison; no hardware access."""
import contextlib,io,json,re,subprocess,struct
from build_gx8002_flash_protection import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,delta,events,output,seed):
    r={f'r{i}':(0x12340000+i+seed)&0xffffffff for i in range(32)}
    r['r0']=output;r['r14']=0x2002f7fc;initial=r.copy();saved=None;index=0;carry=None
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError(f'effect {index}: {kind,address,value} != {e}')
        return e[2]
    def finish():
        if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14)):raise ValueError('return mismatch')
        return r['r0']
    for _ in range(2000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r6, r15' or saved is not None:raise ValueError('frame')
            saved=[r[f'r{i}'] for i in (4,5,6,15)];r['r14']-=16
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None or r['r14']!=initial['r14']-16:raise ValueError('frame')
            for i,v in zip((4,5,6,15),saved):r[f'r{i}']=v
            r['r14']+=16;return finish()
        elif op=='rts':return finish()
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('zextb','zexth'):r[p[0]]=r[p[1]]&(255 if op=='zextb' else 65535)
        elif op in ('addi','subi','addu','subu','and','lsli'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='and' else a<<b if op=='lsli' else a+b)&0xffffffff
        elif op in ('cmpne','cmpnei'):carry=r[p[0]]!=(r[p[1]] if op=='cmpne' else int(p[1],0))
        elif op=='mvcv':r[p[0]]=int(not carry)
        elif op in ('inct','incf'):
            if carry==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('bt','bf','br','bez','bnez'):
            if op in ('bt','bf') and carry is None:raise ValueError('carry')
            if op=='br' or op=='bt' and carry or op=='bf' and not carry or op=='bez' and r[p[0]]==0 or op=='bnez' and r[p[0]]!=0:n=int(p[-1],0)
        elif op in ('ld.w','ld.h','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if op=='st.w':effect('write4',address,r[reg])
            else:r[reg]=effect('read'+str({'ld.w':4,'ld.h':2,'ld.b':1}[op]),address)
        elif op=='bsr':
            result=effect('call',int(args,0)+delta)
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xa5a50000+i+seed)&0xffffffff
            r['r0']=result
        else:raise ValueError('instruction '+op)
        pc=n
    raise ValueError('bound')

def oracle(mode,output,manufacturer,first,second,entries,present,seed):
    d=0x20029000;p=0x20029100;table=0x20029200;e=[]
    if not mode:
        e.append(['write4',output,0])
        if output==d+16:present=0
        elif output==p and present==2:present=1
    e += [['read4',0x200264f0,d],['read4',d+16,p if present else 0]]
    if present:e.append(['read4',p,table if present==2 else 0])
    if mode:return (1 if present==2 else 0xffffffff),e
    result=0xffffffff
    if present==2:
        e += [['call',0x1002375c,1],['read4',0x200264f0,d+0x1000],['read2',d+0x1006,manufacturer]]
        if manufacturer in (0x5e,0x85):
            e += [['call',0x10023734,first],['call',0x10023770,second],['read4',0x200264f0,d+0x2000],['read4',d+0x2010,p+0x2000],['read4',p+0x2004,len(entries)]]
            for i,(a,b,c,f,length) in enumerate(entries):
                base=table+0x2000+i*8
                if output==base+4:length=0
                e += [['read4',p+0x2000,table+0x2000],['read1',base+1,b],['read1',base,a],['read1',base+2,c],['read1',base+3,f],['read4',base+4,length]]
                if first&b==a and second&f==c:result=length;break
    e.append(['write4',output,result]);return (0xffffffff if result==0xffffffff else 0),e

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'protection-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15900','--stop-address=0x159b8',str(wrapper)],text=True))
    # Decode each function section independently.
    cases=0
    for mode,name,entry in [(False,'status',0x15900),(True,'mode',0x15994)]:
        new=decode(subprocess.check_output([str(pre)+'objdump','-d','-j','.text.flash_write_protect_'+name,str(out/'protection.elf')],text=True))
        for manufacturer in (0,0x5e,0x85,0xffff):
            for first in range(256):
                second=first^0xa5
                for entries in ([],[(first,255,second,255,0)],[(first,255,second,255,0xffffffff)],[(256,255,0,0,12),(0,0,0,0,4096)]):
                    # Normalize synthetic entry fields to their byte storage width.
                    entries=[(a&255,b,c,f,l) for a,b,c,f,l in entries]
                    for present in range(3):
                        expected,events=oracle(mode,0x20028000,manufacturer,first,second,entries,present,0)
                        for seed in (0,0xffffffff):
                            if execute(old,entry,0x1000dfec,events,0x20028000,seed)!=expected or execute(new,entry+0x1000dfec,0,events,0x20028000,seed)!=expected:raise ValueError('result')
                            cases+=1
    new=decode(subprocess.check_output([str(pre)+'objdump','-d','-j','.text.flash_write_protect_status',str(out/'protection.elf')],text=True))
    for first in range(256):
        for second in range(256):
            # Reject the first entry by status2, then match both partial masks.
            entries=[(first,255,second^1,255,99),
                     (first&0x5a,0x5a,second&0xa5,0xa5,(first<<8)|second),
                     (0,0,0,0,0xffffffff)]
            expected,events=oracle(False,0x20028000,0x85,first,second,entries,2,0)
            if execute(old,0x15900,0x1000dfec,events,0x20028000,0)!=expected or execute(new,0x100238ec,0,events,0x20028000,0)!=expected:raise ValueError('independent status pair')
            cases+=1
    for output in (0x20029010,0x20029100,0x2002b204,0x2002b20c):
        for first in (0,1,0x5a,0xff):
            for second in (0,1,0xa5,0xff):
                entries=[(first^1,255,second,255,99),(first,255,second,255,0xffffffff)]
                expected,events=oracle(False,output,0x85,first,second,entries,2,0)
                if execute(old,0x15900,0x1000dfec,events,output,0)!=expected or execute(new,0x100238ec,0,events,output,0)!=expected:raise ValueError('output alias')
                cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Both sections fit; admission adapter and reviewed baseline remain pending.', 'Helpers modeled; no hardware qualification; Four valid output aliases covered; exhaustive arbitrary-memory aliasing is not claimed.']}
    (ROOT/'docs/research/gx8002-flash-protection-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
