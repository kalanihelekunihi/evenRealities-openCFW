# SPDX-License-Identifier: MIT
"""Decoded memmove effects; forward memcpy modeled with caller clobbers."""
import json,re,subprocess
from build_gx8002_memmove_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,memory,destination,source,count,copy_code=None,copy_entry=0):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=destination,r1=source,r2=count,r14=0x20070000)
    initial=r.copy();saved=None;condition=False;pc=entry;trace=[]
    for _ in range(count*15+40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],trace
        elif op in ('mov','movi'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addu','subu','addi','subi'):
            left=r[p[0]] if len(p)==2 else r[p[1]]
            right=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(left+right if op.startswith('add') else left-right)&MASK
        elif op in ('cmphs','cmpne'):condition=r[p[0]]>=r[p[1]] if op=='cmphs' else r[p[0]]!=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op in ('ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            if address not in memory:raise ValueError('Unmapped access')
            if op=='ld.b':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg]&255;trace.append(('write',address,memory[address]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0x101d0 else 0))&MASK
            if target!=0x10025738 or (r['r0'],r['r1'],r['r2'])!=(destination,source,count):raise ValueError('Copy call')
            trace.append(('memcpy',destination,source,count))
            if copy_code is None:
                for i in range(count):memory[destination+i]=memory[source+i]
            else:
                from verify_gx8002_memcpy_source import execute as copy_execute
                returned,_=copy_execute(copy_code,memory,destination,source,count,start=copy_entry)
                if returned!=destination:raise ValueError('Nested copy return')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xab000000+i
            r['r0']=destination
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Execution bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x101d0','--stop-address=0x101fc',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-memmove/memmove.disassembly.txt').read_text());cases=0
    for count in (*range(65),127,255):
        for shift in range(-32,33):
            source=0x20030200;destination=source+shift
            memory={a:(a*37+11)&255 for a in range(source-64,source+320)};wanted=memory.copy()
            for i in range(count):wanted[destination+i]=memory[source+i]
            traces=[]
            for code,entry in ((old,0x101d0),(new,0x10206c44)):
                actual=memory.copy();result,trace=execute(code,entry,actual,destination,source,count)
                if result!=destination or actual!=wanted:raise ValueError(('Move mismatch',count,shift))
                traces.append(trace)
            if traces[0]!=traces[1]:raise ValueError('Access order differs')
            cases+=1
    from verify_gx8002_memcpy_source import verify as copy_verify
    copy_evidence=copy_verify()
    copy_old=decode(subprocess.check_output([pre,'-D','--start-address=0x1774c','--stop-address=0x177ca',str(ROOT/'build/gx8002-memcpy-source/stock-analysis.elf')],text=True))
    copy_new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-memcpy-source/copy.o')],text=True))
    nested=0
    for count in (*range(33),63,64,65,127,255):
        for gap in (1,2,3,4,7,16,32):
            source=0x20030200;destination=source-gap
            memory={a:(a*37+11)&255 for a in range(source-64,source+320)}
            wanted=memory.copy()
            for i in range(count):wanted[destination+i]=memory[source+i]
            for code,entry,copy_code,copy_entry in ((old,0x101d0,copy_old,0x1774c),(new,0x10206c44,copy_new,0)):
                actual=memory.copy();result,_=execute(code,entry,actual,destination,source,count,copy_code,copy_entry)
                if actual!=wanted or result!=destination:raise ValueError('Nested forward overlap')
            nested+=1
    return {'nested_cases':nested,'copy_evidence':copy_evidence,'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Forward memcpy decoded in nested cases with modeled caller clobbers. Valid RAM and nonwrapping pointers; admission pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-memmove-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
