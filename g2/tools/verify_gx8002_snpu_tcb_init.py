#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare every decoded descriptor write and preserved ABI against a sparse model."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_tcb_init_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
STATE=0x20027350
OFFSET=0xee60
ADDRESS=0x102058d4

def memory(seed):
    # Include guards and all untouched callback/payload words, not only writes.
    return {STATE+o:(seed ^ (o*0x1020305))&MASK for o in range(-16,0x5a0+16,4)}

def expected(seed):
    trace=[];mem=memory(seed)
    for task in range(10):
        base=STATE+task*144
        for slot in range(8):
            trace.extend([(base+32+slot*12,0x10080+slot),
                          (base+36+slot*12,(base+44+slot*12)&0xfffffff)])
        trace.extend([(base+128,0x10088),(base+16,0x4100ff)])
    for address,value in trace:mem[address]=value
    return trace,mem

def execute(code,pc,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();mem=memory(seed);trace=[];condition=False
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)&MASK
        elif op=='movih':r[p[0]]=(int(p[1],0)<<16)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','mult','lsri','lsli','andni'):
            dst=p[0];left=r[p[1]] if len(p)==3 else r[dst];arg=p[-1]
            right=r[arg] if arg in r else int(arg,0)
            if op in ('addi','addu'):value=left+right
            elif op=='subi':value=left-right
            elif op=='mult':value=left*right
            elif op=='lsri':value=left>>right
            elif op=='lsli':value=left<<right
            else:value=left&~right
            r[dst]=value&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='bseti':r[p[0]]=r[p[1]]|(1<<int(p[2],0))
        elif op=='zext':
            hi,lo=int(p[2],0),int(p[3],0);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('st.w','str.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if m:src,base,offset=m.groups();address=(r[base]+int(offset,0))&MASK
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
                if not m:raise ValueError('TCB store operand')
                src,base,index,shift=m.groups();address=(r[base]+(r[index]<<int(shift)))&MASK
            if address not in mem or not STATE<=address<STATE+0x5a0:raise ValueError('TCB write bounds')
            trace.append((address,r[src]));mem[address]=r[src]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bt':
            if condition:next_pc=int(args,0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:next_pc=int(p[1],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('TCB ABI')
            return trace,mem
        else:raise ValueError('TCB unknown instruction '+op)
        pc=next_pc
    raise ValueError('TCB execution bound')

def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-tcb-init-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xee60','--stop-address=0xeedc',str(w)],text=True))
    new=decode((out/'snpu-tcb-init-candidate.disassembly.txt').read_text());return old,new

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();old,new=programs();cases=0
    for seed in (0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]):
        wanted=expected(seed)
        if execute(old,OFFSET,seed)!=wanted or execute(new,ADDRESS,seed)!=wanted:raise ValueError('TCB write/state mismatch')
        cases+=1
    if not evidence['fits']:raise ValueError('TCB envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':124,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/snpu-tcb-init-candidate.elf',output/'snpu-tcb-init.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'writes_per_case':180,'source_admitted':True,'hardware_qualified':False,'limits':['Fixed shipped ten-record state view. Exact ordered writes, untouched words and guards, and callee-saved ABI compared. No full state ownership or silicon/model execution qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-tcb-init-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
