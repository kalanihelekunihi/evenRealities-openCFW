#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded stock/source comparison for SNPU status processing."""
import json,re,shutil,struct,subprocess
from analyze_gx8002_upstream_objects import sha
from build_gx8002_snpu_process_status_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from model_gx8002_snpu_process_status import MASK,STATE,TARGETS,Case,Model,PrefixReached,expected
OFFSET=0xf164
ADDRESS=0x10205bd8
DELTA=0x101f6a74

def register_list(args):
    result=[]
    for part in args.split(', '):
        match=re.fullmatch(r'r(\d+)(?:-r(\d+))?',part)
        if not match:raise ValueError('status frame register list')
        lo,hi=match.groups();result.extend(range(int(lo),int(hi or lo)+1))
    return result

def execute(code,pc,delta,case):
    model=Model(case);r={f'r{i}':(case.seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc
    initial=r.copy();saved=None;save_bytes=0;local_base=None;stack={};condition=False
    def read(address):
        if local_base is not None and local_base<=address<local_base+12:
            if address&3 or address not in stack:raise ValueError('status uninitialized scratch read')
            return stack[address]
        return model.read(address)
    def write(address,value):
        if local_base is not None and local_base<=address<local_base+12:
            if address&3:raise ValueError('status scratch alignment')
            stack[address]=value&MASK
        else:model.write(address,value)
    def check_call():
        if saved is None or local_base is None or r['r14']!=local_base:raise ValueError('status call frame')
    def clobber(value):
        for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(case.seed^0xcafe0000^model.calls*7919^i)&MASK
        r['r0']=value&MASK
    try:
        for _ in range(30000):
            op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
            if op=='push':
                indices=register_list(args)
                if saved is not None or indices not in ([*range(4,11),15],[*range(4,12),15,16,17]):raise ValueError('status push frame')
                saved={f'r{i}':r[f'r{i}'] for i in indices};save_bytes=4*len(indices)
                if save_bytes!=(44 if delta else 32):raise ValueError('status expected frame size')
                r['r14']-=save_bytes
            elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
            elif op=='mov':r[p[0]]=r[p[1]]
            elif op in ('addi','subi'):
                value=(r[p[0]] if len(p)==2 else r[p[1]]);amount=int(p[-1],0)
                r[p[0]]=(value+(amount if op=='addi' else -amount))&MASK
                if p[0]=='r14' and op=='subi':
                    if saved is None or local_base is not None or amount!=12:raise ValueError('status scratch allocation')
                    local_base=r['r14']
            elif op in ('addu','subu','mult','and'):
                left=r[p[0]] if len(p)==2 else r[p[1]];right=r[p[-1]]
                r[p[0]]={'addu':lambda:left+right,'subu':lambda:left-right,'mult':lambda:left*right,'and':lambda:left&right}[op]()&MASK
            elif op=='divs':
                a=r[p[1]];a=a if a<0x80000000 else a-0x100000000;b=r[p[2]];b=b if b<0x80000000 else b-0x100000000
                if b==0:raise ValueError('status division zero')
                r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
            elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
            elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
            elif op in ('ld.w','st.w'):
                match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
                if not match:raise ValueError('status memory operand')
                reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
                if op=='ld.w':r[reg]=read(address)
                else:write(address,r[reg])
            elif op=='ldr.w':
                match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
                if not match:raise ValueError('status indexed load operand')
                dest,base,index,shift=match.groups();r[dest]=read((r[base]+(r[index]<<int(shift)))&MASK)
            elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
            elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
            elif op=='mvcv':r[p[0]]=int(not condition)
            elif op=='inct':
                if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
            elif op in ('bt','bf'):
                if condition==(op=='bt'):nxt=int(args,0)
            elif op in ('bez','bnez'):
                if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
            elif op=='br':nxt=int(args,0)
            elif op=='bsr':
                check_call();target=(int(args,0)+delta)&MASK
                if target not in TARGETS:raise ValueError('status unknown helper')
                name=TARGETS[target];out=r['r1'];value=model.call(name,r['r0'],r['r1'])
                if name in ('events','completed','overflow_address'):
                    if not local_base<=out<local_base+12 or out&3:raise ValueError('status helper output pointer')
                    stack[out]=value
                    returned=((value&64)<<10) if name=='events' else value
                else:returned=value
                clobber(returned)
            elif op=='jsr':
                check_call();value=model.callback(r[args],r['r0'],r['r1'],r['r2']);clobber(value)
            elif op=='pop':
                if saved is None or set(register_list(args))!={int(k[1:]) for k in saved} or r['r14']!=initial['r14']-save_bytes:raise ValueError('status return frame')
                r.update(saved);r['r14']+=save_bytes
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('status ABI')
                return model.result(r['r0'])
            else:raise ValueError('status unknown instruction '+op)
            pc=nxt
    except PrefixReached:
        check_call();return model.result(None,'ring_prefix')
    raise ValueError('status execution bound')

def cases():
    # Complete low-seven-bit priority combinations, ignored high bits, duplicate
    # completion and callback presence. Ring coordinates stay in valid 0..9.
    for events in range(128):
        for high in (0,0xffffff80):
            for duplicate in (False,True):
                for mask in (0,0x3ff):
                    for mode in ('none','all'):yield Case(events=events|high,duplicate=duplicate,callbacks=mask,mutation=mode,seed=0x12345678)
    for start in range(10):
        for end in range(10):
            for target in range(10):
                for mode in ('none','pointers','callbacks','all'):
                    for mask in (0,0x155,0x3ff):yield Case(start=start,end=end,target=target,callbacks=mask,mutation=mode,seed=MASK if mask else 0)
    for start in range(10):
        for mode in ('none','all'):
            for mask in (0,0x3ff):
                for prefix in (1,11,32):yield Case(start=start,end=(start+3)%10,target=None,callbacks=mask,mutation=mode,prefix=prefix,seed=0x12345678)

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-process-status-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf164','--stop-address=0xf26c',str(w)],text=True));new=decode((out/'snpu-process-status-candidate.disassembly.txt').read_text());count=prefixes=0
    for case in cases():
        wanted=expected(case)
        for code,pc,delta in ((old,OFFSET,DELTA),(new,ADDRESS,0)):
            actual=execute(code,pc,delta,case)
            if actual!=wanted:raise ValueError(f'status trace/state/return mismatch {case} at {pc:#x}')
        if case.prefix:prefixes+=1
        else:count+=1
    if not evidence['fits']:raise ValueError('status envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':264,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-process-status-candidate.elf',output/'snpu-process-status.elf')
    return {'functions':[row],'evidence':evidence,'model_sha256':sha((ROOT/'tools/model_gx8002_snpu_process_status.py').read_bytes()),'cases':count,'noncompletion_prefix_cases':prefixes,'frame_bytes':{'stock':56,'source':44},'source_admitted':True,'hardware_qualified':False,'limits':['Decoded call-boundary model with valid ring indices0..9, all target/start/end positions, callback mutations, helper clobbers, event priorities and observed returns. Scratch stack addresses normalized; pointed-to stack words remain bounds checked. Helper implementations and physical hardware timing are separate obligations. Unmatched descriptor prefixes through32 record visits; no claim of termination. Offset-only state view and descriptor semantics remain incomplete.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-process-status-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
