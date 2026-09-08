#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify driver-exit ordering, callback clearing and fixed success return."""
import json,re,shutil,struct,subprocess
from build_gx8002_stream_shutdown_candidate import ROOT,IMAGE,build,FUNCTIONS
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import sha
MASK=0xffffffff
DELTA=0x101f6a74
CALLBACK=0x20027b50

def execute(code,pc,delta,seed,driver_result):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[];callback=seed
    for _ in range(20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('stream frame')
            saved=r['r15'];r['r14']-=4
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('stream call frame')
            target=(int(args,0)+delta)&MASK
            if target not in (0x10205d40,0x10204984):raise ValueError('stream unknown driver')
            trace.append(['driver',target,'callback_at_entry',callback])
            # Driver may modify the callback during teardown; clear must follow it.
            callback=seed^0xa5a5a5a5
            trace.append(['driver_callback',callback])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            r['r0']=driver_result&MASK
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('stream store operand')
            src,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if address!=CALLBACK:raise ValueError('stream callback address')
            callback=r[src];trace.append(['write',address,callback])
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('stream return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('stream ABI')
            return trace,callback,r['r0']
        else:raise ValueError('unknown stream instruction '+op)
        pc+=width
    raise ValueError('stream execution bound')

def expected(name,seed):
    kws=name=='LvpKwsDone';changed=seed^0xa5a5a5a5
    return ([['driver',0x10205d40 if kws else 0x10204984,'callback_at_entry',seed],['driver_callback',changed]]+([['write',CALLBACK,0]] if kws else []),0 if kws else changed,0)

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'stream-shutdown-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    new=decode((out/'stream-shutdown-candidate.disassembly.txt').read_text());cases=0
    for name,address,offset,size in FUNCTIONS:
        old=decode(subprocess.check_output([pre+'objdump','-D',f'--start-address={offset}',f'--stop-address={offset+size}',str(w)],text=True))
        for seed in (0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678):
            for result in (*range(256),0x7fffffff,0x80000000,0xffffffff):
                for code,pc,delta in ((old,offset,DELTA),(new,address,0)):
                    if execute(code,pc,delta,seed,result)!=expected(name,seed):raise ValueError('stream trace/state/return mismatch')
                cases+=1
    rows=[]
    for region in evidence['regions']:
        if not region['fits']:raise ValueError('stream region size')
        rows.append({'symbol':region['symbol'],'section_name':region['section_name'],'compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-STREAM-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'stream-shutdown-candidate.elf',output/'stream-shutdown.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':4,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,'limits':['Driver exits modeled at call boundaries; their implementation, hardware effects and asynchronous callback timing remain unqualified. Typed callback BSS is source-defined but adds no firmware payload bytes.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-stream-shutdown-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
