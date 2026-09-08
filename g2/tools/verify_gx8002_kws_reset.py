#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check reset/init through decoded memset, including nested frames and source BSS."""
import json,shutil,struct,subprocess
from build_gx8002_kws_reset_candidate import ROOT,IMAGE,FUNCTIONS,build
from build_gx8002_memset_candidate import build as build_memset
from compare_gx8002_memset import execute as fill,expected as expected_fill,decode
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths
DELTA=0x101f6a74
MASK=0xffffffff

def execute(code,entry,delta,fill_code,fill_entry,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;r['r15']=0xf00d0000
    initial=r.copy();stack=[];trace=[];pc=entry;peak=0
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r15':raise ValueError('reset frame')
            stack.append(r['r15']);r['r14']-=4;peak=max(peak,len(stack)*4)
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if not stack:raise ValueError('reset call frame')
            target=(int(args,0)+delta)&MASK;r['r15']=nxt
            if target==0x10208964:
                trace.append(['call','KwsStrategyReset']);nxt=int(args,0)
            elif target==0x102099cc:
                arguments=(r['r0'],r['r1'],r['r2']);trace.append(['call','memset',list(arguments)])
                if arguments!=(0x2002e7a8,0,164):raise ValueError('reset memset extent/value')
                result=fill(fill_code,fill_entry,*arguments,seed)
                trace.extend([['store',*event] for event in result['trace']])
                for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
                r['r0']=result['result']
            else:raise ValueError('unknown reset helper')
        elif op=='pop':
            if args!='r15' or not stack:raise ValueError('reset return frame')
            r['r15']=stack.pop();r['r14']+=4;nxt=r['r15']
            if nxt==initial['r15']:
                if stack or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('reset ABI')
                return {'trace':trace,'peak_frame_bytes':peak}
        else:raise ValueError('unknown reset instruction '+op)
        pc=nxt
    raise ValueError('reset execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();fill_evidence=build_memset();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'kws-reset-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11ef0','--stop-address=0x11f0c',str(w)],text=True))
    old_fill=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x12f58','--stop-address=0x12ff8',str(w)],text=True))
    new=decode((out/'kws-reset-candidate.disassembly.txt').read_text());new_fill=decode((out/'memset-candidate.disassembly.txt').read_text());cases=0
    for n,address,offset,size in FUNCTIONS:
        is_init=n=='KwsStrategyInit'
        want={'trace':([['call','KwsStrategyReset']] if is_init else [])+[['call','memset',[0x2002e7a8,0,164]]]+[['store',*event] for event in expected_fill(0x2002e7a8,0,164)['trace']], 'peak_frame_bytes':8 if is_init else 4}
        for seed in (0,0xffffffff,0x12345678,*[1<<i for i in range(32)]):
            for code,pc,delta,fill_code,fill_pc in ((old,offset,DELTA,old_fill,0x12f58),(new,address,0,new_fill,0x102099cc)):
                if execute(code,pc,delta,fill_code,fill_pc,seed)!=want:raise ValueError('reset continuous trace')
            cases+=1
    rows=[]
    for row in evidence['functions']:
        if not row['fits'] or not row['exact_stock_payload']:raise ValueError('reset envelope/identity')
        rows.append({'symbol':row['symbol'],'section_name':row['section_name'],'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
        'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-KWS-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'kws-reset-candidate.elf',output/'kws-reset.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'evidence':evidence,'memset_build':fill_evidence,'cases':cases,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
      'limits':['Reset/init use fully decoded memset for the164-byte state extent. BSS has a C definition and NOBITS linker allocation; it adds no firmware payload bytes. Startup BSS initialization and whole-decoder/hardware qualification remain separate.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-kws-reset-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
