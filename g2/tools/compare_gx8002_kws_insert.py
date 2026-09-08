#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode activation insertion and compare ordered list traces and float operands."""
import json,re,struct,subprocess
from build_gx8002_kws_insert_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0x2002e7a8
DELTA=0x101f6a74

def signed(v):return v if v<0x80000000 else v-0x100000000
def floating(bits):return struct.unpack('<f',struct.pack('<I',bits))[0]
def less(a,b,override):return floating(a)<floating(b) if override is None else override

def execute(code,pc,delta,memory,arguments,score,seed=0,comparison=None):
    mem=memory.copy();trace=[];r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    for i,value in enumerate(arguments):r[f'r{i}']=value
    r['r14']=0x2002f7fc;initial=r.copy();fr={f'fr{i}':(seed+i)&MASK for i in range(16)};fr['fr0']=score
    saved=None;condition=False
    def read(address):
        if address not in mem:raise ValueError('activation read outside list')
        value=mem[address];trace.append(['read',address,value]);return value
    def write(address,value):
        if address not in mem:raise ValueError('activation write outside list')
        mem[address]=value;trace.append(['write',address,value])
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('activation frame')
            saved=r['r15'];r['r14']-=4
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='mult':r[p[0]]=(r[p[1]]*r[p[2]])&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='ldbi.w':
            match=re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not match:raise ValueError('activation postincrement operand')
            dst,base=match.groups();address=r[base];r[dst]=read(address);r[base]=(address+4)&MASK
        elif op in ('ld.w','st.w','flds','fsts'):
            match=re.fullmatch(r'((?:fr|r)\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('activation memory operand')
            reg,base,offset=match.groups();address=(r[base]+int(offset,0))&MASK
            if op=='ld.w':r[reg]=read(address)
            elif op=='flds':fr[reg]=read(address)
            else:write(address,(fr if op=='fsts' else r)[reg])
        elif op=='str.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match:raise ValueError('activation indexed store')
            reg,base,index,shift=match.groups();write((r[base]+(r[index]<<int(shift)))&MASK,r[reg])
        elif op=='fcmplts':
            a,b=fr[p[0]],fr[p[1]];condition=less(a,b,comparison);trace.append(['fcmplts',a,b,condition])
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('activation call frame')
            if (int(args,0)+delta)&MASK!=0x10206c24 or r['r0']!=0x1020b34f:raise ValueError('activation overflow logging')
            trace.append(['printf',r['r0']])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            for i in range(16):fr[f'fr{i}']=(seed^0xdead0000^i)&MASK
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('activation return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('activation ABI')
            return {'trace':trace,'memory':mem}
        else:raise ValueError('unknown activation instruction '+op)
        pc=nxt
    raise ValueError('activation execution bound')

def expected(memory,arguments,score,comparison=None):
    mem=memory.copy();trace=[];index,value,score_index,private=arguments
    def read(a):trace.append(['read',a,mem[a]]);return mem[a]
    def write(a,v):mem[a]=v;trace.append(['write',a,v])
    total=read(BASE)
    for i in range(max(0,signed(total))):
        if i>=8:raise ValueError('activation count outside valid storage')
        a=BASE+4+20*i
        if read(a+4)==value and read(a)==index:
            old=read(a+8);condition=less(old,score,comparison);trace.append(['fcmplts',old,score,condition])
            if condition:write(a+8,score)
            return {'trace':trace,'memory':mem}
    if total>=8:trace.append(['printf',0x1020b34f])
    else:
        a=BASE+4+20*total
        for offset,v in ((0,index),(4,value),(8,score),(12,score_index),(16,private)):write(a+offset,v)
        write(BASE,total+1)
    return {'trace':trace,'memory':mem}

def fixture(total,match,old_score,seed=0):
    m={BASE+4*i:(seed+i*0x1020304)&MASK for i in range(41)};m[BASE]=total
    for i in range(8):m[BASE+4+20*i]=i;m[BASE+8+20*i]=i+100;m[BASE+12+20*i]=old_score
    if match is not None:m[BASE+4+20*match]=55;m[BASE+8+20*match]=66
    return m

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'kws-insert-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    data=bytearray(w.read_bytes());struct.pack_into('<I',data,36,0x21006009);w.write_bytes(data)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11f0c','--stop-address=0x11f9c',str(w)],text=True))
    new=decode((out/'kws-insert-candidate.disassembly.txt').read_text());cases=0;symbolic=0
    def check(mem,score,seed,comparison=None):
        args=(55,66,seed,seed^MASK);want=expected(mem,args,score,comparison)
        for code,pc,delta in ((old,0x11f0c,DELTA),(new,0x10208980,0)):
            if execute(code,pc,delta,mem,args,score,seed,comparison)!=want:raise ValueError('activation trace mismatch')
    scores=(0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f000000,0x3f800000,0x40000000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00001,0xffc12345,0x7f800001)
    for total in range(9):
     for match in (None,*range(total)):
      for old_score in scores:
       for score in scores:
        for seed in (0,0xffffffff):
         check(fixture(total,match,old_score,seed),score,seed);cases+=1
    for count in (0xffffffff,0x80000000,0xfffffffe):
     for seed in (0,0xffffffff):check(fixture(count,None,0,seed),0,seed);cases+=1
    for count in range(1,9):
     for seed in (0,0xffffffff):
      for last_matches in (False,True):
       m=fixture(count,None,0x3f800000,seed)
       for n in range(count):m[BASE+8+20*n]=66
       if last_matches:m[BASE+4+20*(count-1)]=55
       check(m,0x40000000,seed);cases+=1
    # Same instruction/operands must preserve either condition outcome, without
    # claiming a particular hardware NaN, denormal or floating-control setting.
    for old_score in scores:
     for score in scores:
      for condition in (False,True):
       m=fixture(8,3,old_score);m[BASE+4+20*6]=55;m[BASE+8+20*6]=66
       check(m,score,0x12345678,condition);symbolic+=1
    report={'build':evidence,'cases':cases,'symbolic_float_condition_cases':symbolic,'frame_bytes':4,'source_admitted':False,
      'limits':['Valid list counts0..8 and negative-count logging only. Positive corrupted counts above8 can read beyond the list before capacity checking. IEEE model plus both comparison outcomes with identical raw operands; no physical FP control/status or timing claim. Storage and overflow message remain separate retained dependencies.']}
    (ROOT/'docs/research/gx8002-kws-insert-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
