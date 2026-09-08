#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify overtime reset composed with decoded diagnostic dump calls."""
import json,re,shutil,struct,subprocess
from analyze_gx8002_upstream_objects import sha
from build_gx8002_snpu_overtime_candidate import ROOT,IMAGE,build
from verify_gx8002_snpu_dump import execute as execute_dump, verify as verify_dump
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from model_gx8002_snpu_overtime import MASK,STATE,TARGETS,Case,Model,expected
ADDRESS=0x10205b1c
OFFSET=0xf0a8
DELTA=0x101f6a74

def execute(code,pc,delta,case):
    model=Model(case);r={f'r{i}':(case.seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;save_bytes=0;local=None;scratch={}
    def clobber(value):
        for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(case.seed^0xbeef0000^model.calls*7919^i)&MASK
        r['r0']=value&MASK
    def read(address,byte=False):
        if local is not None and local<=address<local+16:
            if byte or address&3 or address not in scratch:raise ValueError('overtime scratch read')
            return scratch[address]
        if address in model.memory:return model.read_state(address)
        return model.read_byte(address) if byte else model.read_word(address)
    for _ in range(120):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':
            wanted='r4-r6, r15' if delta else 'r4-r5, r15'
            if saved is not None or args!=wanted:raise ValueError('overtime push frame')
            indices=(*range(4,7 if delta else 6),15);saved={f'r{i}':r[f'r{i}'] for i in indices};save_bytes=4*len(indices);r['r14']-=save_bytes
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='movih':r[p[0]]=(int(p[1],0)<<16)&MASK
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            value=r[p[0]] if len(p)==2 else r[p[1]];amount=int(p[-1],0);r[p[0]]=(value+(amount if op=='addi' else -amount))&MASK
            if p[0]=='r14' and op=='subi':
                if saved is None or local is not None or amount!=16:raise ValueError('overtime scratch allocation')
                local=r['r14']
        elif op=='addu':r[p[0]]=((r[p[0]]+r[p[1]]) if len(p)==2 else (r[p[1]]+r[p[2]]))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op in ('ld.w','ld.b','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('overtime memory operand')
            reg,base,offset=match.groups();address=(r[base]+int(offset,0))&MASK
            if op=='st.w':
                if local is None or not local<=address<local+16 or address&3:raise ValueError('overtime scratch store')
                scratch[address]=r[reg]
            else:r[reg]=read(address,op=='ld.b')
        elif op=='ldr.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match:raise ValueError('overtime indexed operand')
            reg,base,index,shift=match.groups();r[reg]=read((r[base]+(r[index]<<int(shift)))&MASK)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            if saved is None or local is None or r['r14']!=local:raise ValueError('overtime call frame')
            target=(int(args,0)+delta)&MASK
            if target==0x10206c24:value=model.printf(r['r0'],r['r1'],r['r2'],r['r3'])
            elif target==0x10205ad8:
                model.trace.append(['dump',r['r0']])
                _,value=execute_dump(code,target-delta,delta,r['r0'],case.seed,case.changing,model.read_word,model.printf,stack_top=r['r14'])
            elif target in TARGETS:
                name=TARGETS[target];out=r['r2'] if name=='base' else r['r1'];value=model.call(name,r['r0'],r['r1'])
                if name in ('base','current','previous','head'):
                    if not local<=out<local+16 or out&3:raise ValueError('overtime getter output pointer')
                    scratch[out]=value
            else:raise ValueError('overtime helper target')
            clobber(value)
        elif op=='pop':
            wanted='r4-r6, r15' if delta else 'r4-r5, r15'
            if saved is None or args!=wanted or r['r14']!=initial['r14']-save_bytes:raise ValueError('overtime return frame')
            r.update(saved);r['r14']+=save_bytes
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('overtime ABI')
            return model.result()
        else:raise ValueError('overtime unknown instruction '+op)
        pc=nxt
    raise ValueError('overtime execution bound')

def cases():
    values=(0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)])
    for current in (0x30080,0x40080,0x50080):
        for previous in (0,0x31000):
            for head in values:
                for seed in (0,MASK,0x12345678):
                    for changing,pointers in ((False,False),(True,False),(False,True),(True,True)):
                        yield Case(seed,current,previous,head,changing,pointers)

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);dump_report=verify_dump();evidence=dump_report['evidence'];out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-overtime-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf064','--stop-address=0xf164',str(w)],text=True));new=decode((out/'snpu-overtime-candidate.disassembly.txt').read_text());count=0
    for case in cases():
        wanted=expected(case)
        for code,pc,delta in ((old,OFFSET,DELTA),(new,ADDRESS,0)):
            if execute(code,pc,delta,case)!=wanted:raise ValueError(f'overtime trace/state mismatch {case} at {pc:#x}')
        count+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('overtime envelope')
        row={k:region[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        if 'ownership_kind' in region:row['ownership_kind']=region['ownership_kind']
        row['stock_occurrences']=[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text' if region.get('ownership_kind')!='generated_source_data' else 'image_a_rodata'}];rows.append(row)
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-overtime-candidate.elf',output/'snpu-overtime.elf')
    return {'functions':rows,'evidence':evidence,'model_sha256':sha((ROOT/'tools/model_gx8002_snpu_overtime.py').read_bytes()),'dump_verifier_sha256':sha((ROOT/'tools/verify_gx8002_snpu_dump.py').read_bytes()),'cases':count,'dump_cases':dump_report['cases'],'frame_bytes':{'stock':32,'source':28,'nested_dump':24},'source_admitted':True,'hardware_qualified':False,'limits':['Decoded reset composed with decoded dumps; scratch addresses normalized but bounds/initialization checked. Both head paths, changing aligned RAM data, pointer mutations at every helper/printf boundary, caller clobbers and restart ordering modeled. Helper MMIO internals have separate qualification; physical address validity/timing unqualified. Command/state semantics remain partially recovered.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-overtime-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
