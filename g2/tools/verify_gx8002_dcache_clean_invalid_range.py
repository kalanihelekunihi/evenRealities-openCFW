#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded cache-clean ordered MMIO and leaf ABI qualification."""
import json,re,shutil,struct,subprocess
from build_gx8002_dcache_clean_invalid_range_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
OFFSET=0x176d4
ADDRESS=0x100256c0
PORT=0xe000f004

def signed(x):return x if x<0x80000000 else x-0x100000000

def expected(pointer,size,limit=None):
    count=(max(0,signed(size&MASK))+15)//16
    if limit is not None:count=min(count,limit)
    return [(PORT,(((pointer&0xfffffff0)|10)+i*16)&MASK) for i in range(count)]

def execute(code,pc,pointer,size,seed,limit=None,stack_top=0x2002f7fc):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    r['r0']=pointer;r['r1']=size&MASK;r['r14']=stack_top;initial=r.copy();trace=[];condition=False
    for _ in range(100000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)&MASK
        elif op in ('addi','subi','addu','subu','and','andni','ori'):
            dst=p[0];a=r[p[1]] if len(p)==3 else r[dst];arg=p[-1];b=r[arg] if arg in r else int(arg,0)
            if op in ('addi','addu'):v=a+b
            elif op in ('subi','subu'):v=a-b
            elif op=='and':v=a&b
            elif op=='andni':v=a&~b
            else:v=a|b
            r[dst]=v&MASK
        elif op=='cmplti':condition=signed(r[p[0]])<int(p[1],0)
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='bhz':
            if signed(r[p[0]])>0:nxt=int(p[1],0)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('cache store operand')
            src,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if address!=PORT:raise ValueError('cache MMIO address')
            trace.append((address,r[src]))
            if limit is not None and len(trace)==limit:return trace,False
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('cache leaf ABI')
            return trace,True
        else:raise ValueError('cache unknown instruction '+op)
        pc=nxt
    raise ValueError('cache execution bound')

def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'dcache-clean-invalid-range-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x176d4','--stop-address=0x17730',str(w)],text=True))
    return old,decode((out/'dcache-clean-invalid-range-candidate.disassembly.txt').read_text())

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();old,new=programs();cases=0;prefix_cases=0
    pointers=[base+low for base in (0,0x20027350,0xfffffff0) for low in range(16)]
    sizes=(*range(0,258),511,512,513,4095,4096,4097,MASK,0x80000000,0x80000001,0xffffff80)
    for pointer in pointers:
        for size in sizes:
            seed=(pointer^size)&MASK;wanted=(expected(pointer,size),True)
            if execute(old,OFFSET,pointer,size,seed)!=wanted or execute(new,ADDRESS,pointer,size,seed)!=wanted:raise ValueError('cache full trace/ABI mismatch')
            cases+=1
        for size in (0x7fffffff,0x40000000,0x10000001):
            wanted=(expected(pointer,size,65),False)
            if execute(old,OFFSET,pointer,size,0,65)!=wanted or execute(new,ADDRESS,pointer,size,0,65)!=wanted:raise ValueError('cache prefix mismatch')
            prefix_cases+=1
    if not evidence['fits']:raise ValueError('cache envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':92,'sha256':evidence['stock_sha256'],'region':'image_a_sram_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/dcache-clean-invalid-range-candidate.elf',output/'dcache-clean-invalid-range.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'prefix_cases':prefix_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Signed-size and exact MMIO trace comparison; moderate sizes complete, huge positives only 65-write prefixes. Void API: incidental r0 excluded. No physical address/cache coherence or timing qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-dcache-clean-invalid-range-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
