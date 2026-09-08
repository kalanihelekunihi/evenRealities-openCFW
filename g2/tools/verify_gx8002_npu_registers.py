#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare stock, native instruction wrappers and defined portable register C."""
import json,re,shutil,struct,subprocess
from build_gx8002_npu_register_candidate import ROOT,IMAGE,FUNCTIONS,DELTA,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff

def expected(name,address,value,argument):
    count=argument&63;trace=[];result=None;after=value
    if name!='set_value':trace.append(['read',address,value])
    if name=='get_bit':result=((value>>count)&1) if count<32 else 0
    elif name=='set_bit':after=value|((1<<count) if count<32 else 0)
    elif name=='clear_bit':after=value&(~(1<<count)&MASK) if count<32 else 0
    elif name=='get_value':result=value
    elif name=='set_value':after=argument
    else:raise ValueError('register oracle function')
    if name in ('set_bit','clear_bit','set_value'):trace.append(['write',address,after])
    return trace,after,result

def execute(code,pc,name,address,value,argument,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=address;r['r1']=argument;r['r14']=0x2002f7fc;initial=r.copy();trace=[];after=value
    for _ in range(40):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('and','or'):r[p[0]]=(r[p[0]]&r[p[1]]) if op=='and' else (r[p[0]]|r[p[1]])
        elif op in ('lsr','lsl','rotl'):
            source=r[p[0]] if len(p)==2 else r[p[1]];count=r[p[-1]]&63
            if count>=32:result=0
            elif op=='lsr':result=source>>count
            elif op=='lsl':result=(source<<count)&MASK
            else:result=((source<<count)|(source>>((32-count)&31)))&MASK
            r[p[0]]=result
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('NPU register memory operand')
            reg,base,off=m.groups();effective=(r[base]+int(off,0))&MASK
            if effective!=address or effective&3:raise ValueError('NPU register MMIO address/alignment')
            if op=='ld.w':r[reg]=value;trace.append(['read',effective,value])
            else:after=r[reg];trace.append(['write',effective,after])
        elif op=='bnez':
            if r[p[0]]!=0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('NPU register ABI/frame')
            return trace,after,r['r0'] if name in ('get_bit','get_value') else None
        else:raise ValueError('unknown NPU register instruction '+op)
        pc=nxt
    raise ValueError('NPU register execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'npu-register-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xeb4c','--stop-address=0xeb80',str(w)],text=True));native=decode((out/'npu-register-native.disassembly.txt').read_text());portable=decode((out/'npu-register-portable.disassembly.txt').read_text());cases=0
    values=[0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    counts=[*range(64),*[(1<<i)|low for i in range(6,32) for low in (0,31,32,63)],MASK,0x12345678]
    for index,(name,offset,size) in enumerate(FUNCTIONS):
      for value in values:
       for argument in (counts if name.endswith('bit') else values):
        for address,seed in ((0xa0b00000,0),(0xfffffffc,MASK)):
         wanted=expected(name,address,value,argument)
         for code,pc in ((old,offset),(native,offset+DELTA),(portable,0x10300000+index*0x100)):
          if execute(code,pc,name,address,value,argument,seed)!=wanted:raise ValueError('NPU register trace/value mismatch')
         cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('NPU register envelope')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256','ownership_kind')};row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'npu-register-native.elf',output/'npu-register.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':0,'source_admitted':True,'hardware_qualified':False,'limits':['Native, portable-C and stock decoded comparison uses documented C-SKY low-six-bit shift/rotate semantics. Aligned modeled word accesses; no physical MMIO semantics or target execution proof. Three instruction-wrapper functions are counted as compiled_assembly, not pure C. Portable image is comparison-only.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-npu-register-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
