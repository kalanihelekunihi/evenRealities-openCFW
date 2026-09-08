#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded stock/source mode code and independent state/callback traces."""
import json, re, struct, subprocess
from build_gx8002_mode_candidate import ROOT, IMAGE, BINDINGS, FUNCTIONS, build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=BINDINGS['open_cfw_gx8002_mode_state']; LIST=BINDINGS['open_cfw_gx8002_mode_list']
INFOS=(BINDINGS['lvp_idle_mode_info'],BINDINGS['lvp_tws_mode_info'])

def memory():
    data=IMAGE.read_bytes(); m={}
    for a,size in ((LIST,8),*( (a,20) for a in INFOS)):
        for offset in range(0,size,4):m[a+offset]=struct.unpack_from('<I',data,a+offset-0x101f6a74)[0]
    if [m[LIST+4*i] for i in range(2)]!=list(INFOS) or [m[a] for a in INFOS]!=[0,1]:raise ValueError('mode table identification')
    m[STATE]=0; m[STATE+4]=0
    return m

def execute(code,pc,mem,argument,changes,seed=0,kind='init'):
    mem=mem.copy(); trace=[]; changes=list(changes); call_index=0
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;r['r0']=argument
    initial=r.copy();saved=None;condition=False
    def read(a):
        if a not in mem:raise ValueError('unknown mode read')
        value=mem[a];trace.append(['read',a,value]);return value
    for _ in range(150):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            wanted='r4-r5, r15' if kind=='init' else 'r4, r15'
            if saved is not None or args!=wanted:raise ValueError('mode frame')
            names=(4,5,15) if kind=='init' else (4,15)
            saved={n:r[f'r{n}'] for n in names};r['r14']-=4*len(names)
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('mode memory operand')
            reg,base,off=match.groups();a=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=read(a)
            else:
                if a not in (STATE,STATE+4):raise ValueError('unknown mode write')
                mem[a]=r[reg];trace.append(['write',a,r[reg]])
        elif op=='ldr.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match:raise ValueError('mode indexed operand')
            dst,base,index,shift=match.groups();r[dst]=read((r[base]+(r[index]<<int(shift)))&MASK)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='jsr':
            if saved is None or r['r14']!=initial['r14']-4*len(saved):raise ValueError('mode call frame')
            target=r[args];field=12 if kind=='tick' else (16 if call_index==0 else 4)
            if target==0 or target not in [mem[a+field] for a in INFOS]:raise ValueError('wrong mode callback')
            if kind=='init' and call_index==1 and r['r0']!=65535:raise ValueError('mode init flag')
            trace.append(['call',target,[65535] if kind=='init' and call_index==1 else []])
            if call_index>=len(changes):raise ValueError('extra mode callback')
            index,loop=changes[call_index];call_index+=1
            if index is not None:mem[STATE+4]=index
            if loop is not None:mem[STATE]=loop
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
        elif op=='pop':
            wanted='r4-r5, r15' if kind=='init' else 'r4, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-4*len(saved):raise ValueError('mode return frame')
            for n,v in saved.items():r[f'r{n}']=v
            r['r14']+=4*len(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('mode ABI')
            if call_index!=len(changes):raise ValueError('unused mode callback changes')
            return {'trace':trace,'result':r['r0'],'state':[mem[STATE],mem[STATE+4]]}
        else:raise ValueError('unknown mode instruction '+op)
        pc=nxt
    raise ValueError('mode execution bound')

def expected(mem,argument,changes,kind):
    m=mem.copy();trace=[];ci=0
    def read(a):trace.append(['read',a,m[a]]);return m[a]
    def write(a,v):m[a]=v;trace.append(['write',a,v])
    def call(field,args):
        nonlocal ci
        target=read(read(LIST+4*read(STATE+4))+field)
        if target:
            trace.append(['call',target,args]);index,loop=changes[ci];ci+=1
            if index is not None:m[STATE+4]=index
            if loop is not None:m[STATE]=loop
    if kind=='init':
        first=read(INFOS[0]);write(STATE,1);write(STATE+4,0)
        if argument==first:write(STATE+4,0)
        elif argument==read(INFOS[1]):write(STATE+4,1)
        call(16,[]);call(4,[65535]);result=read(read(LIST+4*read(STATE+4)))
    else:call(12,[]);result=read(STATE)
    return {'trace':trace,'result':result,'state':[m[STATE],m[STATE+4]]}

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'mode-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11b30','--stop-address=0x11ba8',str(w)],text=True));new=decode((out/'mode-candidate.disassembly.txt').read_text())
    counts={'init':0,'tick':0};base=memory()
    def check(kind,arg,m,changes,seed):
        row=FUNCTIONS[0 if kind=='init' else 1];want=expected(m,arg,changes,kind)
        for code,entry in ((old,row[2]),(new,row[1])):
            got=execute(code,entry,m,arg,changes,seed,kind)
            if got!=want:raise ValueError(f'mode {kind} mismatch: {got} != {want}')
        counts[kind]+=1
    values=(0,1,2,3,0xffff,0x7fffffff,0x80000000,0xffffffff,*[1<<i for i in range(2,31)])
    for arg in values:
     for first in (None,0,1):
      for second in (None,0,1):
       for loop in (0,1,0x80000000,0xffffffff):
        for seed in (0,0xffffffff):
         m=base.copy();m[STATE]=seed;m[STATE+4]=seed
         check('init',arg,m,[(first,loop),(second,loop^MASK)],seed)
    for index in (0,1):
     for present in (False,True):
      for loop in (0,1,2,0x80000000,0xffffffff):
       for next_index in (None,0,1):
        for next_loop in (None,0,1,0xffffffff):
         for seed in (0,0xffffffff):
          m=base.copy();m[STATE]=loop;m[STATE+4]=index
          if not present:m[INFOS[index]+12]=0
          check('tick',seed,m,[(next_index,next_loop)] if present else [],seed)
    report={'build':evidence,'cases':counts,'frame_bytes':{'init':12,'tick':8},'source_admitted':False,
            'limits':['Returning callback model with adversarial caller-register clobbers, live loop values, and valid index changes. Invalid callback-produced indices outside the recovered two-entry table are not qualified. Mode callbacks/table/state ownership and hardware execution remain separate.']}
    (ROOT/'docs/research/gx8002-mode-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
