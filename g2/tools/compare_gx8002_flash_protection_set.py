#!/usr/bin/env python3
"""Ordered decoded protection-query comparison; no hardware access."""
import contextlib,io,json,re,subprocess,struct
from build_gx8002_flash_protection_set import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,delta,events,requested,output,seed):
    r={f'r{i}':(0x12340000+i+seed)&0xffffffff for i in range(32)}
    r['r0']=requested;r['r1']=output;r['r14']=0x2002f7fc;initial=r.copy();saved=None;index=0;carry=None;local={}
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
            if args!='r4-r10, r15' or saved is not None:raise ValueError('frame')
            saved=[r[f'r{i}'] for i in (4,5,6,7,8,9,10,15)];r['r14']-=32
        elif op=='pop':
            if args!='r4-r10, r15' or saved is None or r['r14']!=initial['r14']-32:raise ValueError('frame')
            for i,v in zip((4,5,6,7,8,9,10,15),saved):r[f'r{i}']=v
            r['r14']+=32;return finish()
        elif op=='rts':return finish()
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('zextb','zexth'):r[p[0]]=r[p[1]]&(255 if op=='zextb' else 65535)
        elif op in ('addi','subi','addu','subu','and','andn','or','lsli','lsri'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a&b if op=='and' else a&~b if op=='andn' else a|b if op=='or' else a<<b if op=='lsli' else a>>b if op=='lsri' else a+b)&0xffffffff
        elif op in ('cmpne','cmpnei'):carry=r[p[0]]!=(r[p[1]] if op=='cmpne' else int(p[1],0))
        elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&0xffffffff
        elif op=='cmphs':carry=r[p[0]]>=r[p[1]]
        elif op=='mvc':r[p[0]]=int(carry)
        elif op=='mvcv':r[p[0]]=int(not carry)
        elif op in ('inct','incf'):
            if carry==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('bt','bf','br','bez','bnez'):
            if op in ('bt','bf') and carry is None:raise ValueError('carry')
            if op=='br' or op=='bt' and carry or op=='bf' and not carry or op=='bez' and r[p[0]]==0 or op=='bnez' and r[p[0]]!=0:n=int(p[-1],0)
        elif op in ('ld.w','ld.h','ld.b','st.w','st.h','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            size={'w':4,'h':2,'b':1}[op[-1]]
            if initial['r14']-40<=address<initial['r14']-32:
                if address+size>initial['r14']-32:raise ValueError('stack bounds')
                if op.startswith('st.'):
                    for j in range(size):local[address+j]=(r[reg]>>(8*j))&255
                else:
                    if any(address+j not in local for j in range(size)):raise ValueError('uninitialized stack')
                    r[reg]=sum(local[address+j]<<(8*j) for j in range(size))
            elif op.startswith('st.'):effect('write'+str(size),address,r[reg]&((1<<(size*8))-1))
            else:r[reg]=effect('read'+str(size),address)
        elif op=='bsr':
            target=int(args,0)+delta
            result=effect('call',target)
            if target==0x100236dc:
                if (r['r0'],r['r1'],r['r2'])!=(1,initial['r14']-40,2):raise ValueError('command arguments')
                if [local.get(r['r1']+i) for i in range(2)]!=result['command']:raise ValueError('command bytes')
                result=result['return']
            elif target==0x100238ec:
                if r['r0']!=initial['r14']-36:raise ValueError('status output argument')
                for j in range(4):local[r['r0']+j]=(result['observed']>>(8*j))&255
                result=result['return']
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xa5a50000+i+seed)&0xffffffff
            r['r0']=result
        else:raise ValueError('instruction '+op)
        pc=n
    raise ValueError('bound')

def oracle(requested,manufacturer,first,second,entries,present,status_return,observed,output=0x20028000):
    d=0x20029000;p=0x20029100;table=0x20029200
    e=[['read4',0x200264f0,d],['read4',d+16,p if present else 0],['write4',output,0]]
    if output==p and present==2:present=1
    if output==d+4:manufacturer=0
    if present:e.append(['read4',p,table if present==2 else 0])
    if present!=2:return (0xffffffff if requested else 0),e
    e += [['read4',d+4,manufacturer<<16],['call',0x1002375c,1],['read4',0x200264f0,d+0x1000],['read4',d+0x1010,p+0x1000],['read4',p+0x1000,table+0x1000],['read4',p+0x1004,len(entries)]]
    v1=v2=m1=m2=0
    for i,(a,b,c,f,length) in enumerate(entries):
        base=table+0x1000+i*8
        if output==base+4:length=0
        e.append(['read4',base+4,length])
        if requested<length:break
        e += [['read1',base,a],['read1',base+2,c],['read1',base+1,b],['read1',base+3,f]]
        v1,m1,v2,m2=a,b,c,f
    if manufacturer not in (0x5e,0x85):return 0xffffffff,e
    command=[((first&~m1)|v1)&255,((second&~m2)|v2)&255]
    e += [['call',0x10023734,first],['call',0x10023770,second],['call',0x1002375c,1],['call',0x1002374c,0],['call',0x100236dc,{'command':command,'return':0}],['call',0x1002375c,1],['call',0x100238ec,{'observed':observed,'return':status_return}]]
    if status_return==0xffffffff:return 0xffffffff,e
    e.append(['write4',output,observed]);return 0,e

def execute_wrapper(code,pc,delta,argument,expected_argument,result):
    r={f'r{i}':0x12340000+i for i in range(32)}
    r['r0']=argument;r['r14']=0x2002f7fc;initial=r.copy();saved=None;calls=0
    for _ in range(20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('wrapper frame')
            saved=r['r15'];r['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None or r['r14']!=initial['r14']-4:raise ValueError('wrapper frame')
            r['r15']=saved;r['r14']+=4
            if calls!=1 or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('wrapper return')
            return r['r0']
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[1]]+(1 if op=='addi' else -1)*int(p[2],0))&0xffffffff
        elif op=='bsr':
            if int(args,0)+delta!=0x100239a4 or calls or (r['r0'],r['r1'],r['r14'])!=(expected_argument,initial['r14']-8,initial['r14']-8):raise ValueError('wrapper call')
            calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xa5a50000+i
            r['r0']=result
        else:raise ValueError('wrapper opcode '+op)
        pc=n
    raise ValueError('wrapper bound')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'protection-set-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x159b8','--stop-address=0x15a84',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(pre)+'objdump','-d','-j','.text.flash_write_protect_set',str(out/'protection-set.elf')],text=True));cases=0
    tables=[[],[(0,0,0,0,0)],[(1,0x5a,0x80,0xa5,4096),(0,255,2,255,8192)],[(7,255,9,255,8192),(3,255,4,255,1)]]
    for requested in (0,1,4095,4096,8191,8192,0x7fffffff,0x80000000,0xffffffff):
        for manufacturer in (0,0x5e,0x85,0xffff):
            for first in (0,1,0x55,0xaa,0xff):
                for entries in tables:
                    for present in range(3):
                        for status_return in (0,0xffffffff,1):
                            expected,events=oracle(requested,manufacturer,first,first^0xa5,entries,present,status_return,0xabcdef01)
                            for seed in (0,0xffffffff):
                                if execute(old,0x159b8,0x1000dfec,events,requested,0x20028000,seed)!=expected or execute(new,0x100239a4,0,events,requested,0x20028000,seed)!=expected:raise ValueError('result')
                                cases+=1
    for first in range(256):
        for second in range(256):
            entries=[(first^0x5a,first,second^0xa5,second,0)]
            expected,events=oracle(0,0x85,first,second,entries,2,0,0x12345678)
            if execute(old,0x159b8,0x1000dfec,events,0,0x20028000,0)!=expected or execute(new,0x100239a4,0,events,0,0x20028000,0)!=expected:raise ValueError('status pair')
            cases+=1
    old_wrappers=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15a84','--stop-address=0x15aa4',str(wrapper)],text=True))
    wrapper_cases=0
    for name,entry in [('lock',0x15a84),('unlock',0x15a94)]:
        new_wrapper=decode(subprocess.check_output([str(pre)+'objdump','-d','-j','.text.flash_write_protect_'+name,str(out/'protection-set.elf')],text=True))
        for argument in (0,1,4096,0x7fffffff,0x80000000,0xffffffff):
            for result in (0,1,0x7fffffff,0x80000000,0xffffffff):
                wanted=argument if name=='lock' else 0
                if execute_wrapper(old_wrappers,entry,0x1000dfec,argument,wanted,result)!=result or execute_wrapper(new_wrapper,entry+0x1000dfec,0,argument,wanted,result)!=result:raise ValueError('wrapper mismatch')
                wrapper_cases+=1
    alias_cases=0
    for output in (0x20029100,0x20029004,0x2002a204,0x20029010):
        for requested in (0,1,4096,0xffffffff):
            for status_return in (0,0xffffffff):
                expected,events=oracle(requested,0x85,0xa5,0x5a,[(3,255,4,255,4096)],2,status_return,8192,output)
                if execute(old,0x159b8,0x1000dfec,events,requested,output,0)!=expected or execute(new,0x100239a4,0,events,requested,output,0)!=expected:raise ValueError('alias mismatch')
                alias_cases+=1
    report={'build':evidence,'cases':cases,'wrapper_cases':wrapper_cases,'alias_cases':alias_cases,'source_admitted':False,'limits':['Helpers modeled; 60 wrapper cases and four output-alias locations qualified; no physical hardware qualification.', 'Private stack initialization uses two stock byte stores versus one source halfword store; command bytes and 40-byte frame checked.']}
    (ROOT/'docs/research/gx8002-flash-protection-set-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
