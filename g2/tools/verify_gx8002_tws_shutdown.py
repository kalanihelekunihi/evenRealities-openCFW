#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify TWS lifecycle wrappers against independent helper-call contracts."""
import json,shutil,struct,subprocess
from build_gx8002_tws_shutdown_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import sha
MASK=0xffffffff
DELTA=0x101f6a74

def execute(code,pc,delta,seed,helper_result):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[]
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('TWS lifecycle frame')
            saved=r['r15'];r['r14']-=4
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('TWS lifecycle call frame')
            target=(int(args,0)+delta)&MASK
            if target==0x102099cc:trace.append(['memset',r['r0'],r['r1'],r['r2']])
            elif target==0x10206dac:trace.append(['LvpKwsDone'])
            elif target==0x102073f8:trace.append(['LvpAudioInDone'])
            elif target==0x10206dc0:trace.append(['LvpInitBuffer'])
            elif target==0x10206c24:trace.append(['printf',r['r0']])
            else:raise ValueError('TWS lifecycle unknown helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            r['r0']=helper_result&MASK
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('TWS lifecycle return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('TWS lifecycle ABI')
            return trace,r['r0']
        else:raise ValueError('unknown TWS lifecycle instruction '+op)
        pc+=width
    raise ValueError('TWS lifecycle execution bound')

def expected(kind,result):
    if kind=='buffer':return [['LvpInitBuffer']],result&MASK
    return [['memset',0x2002e6ec,0,20],['LvpKwsDone'],['LvpAudioInDone'],['printf',0x1020b218]],None

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'tws-shutdown-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11bd0','--stop-address=0x11bfc',str(w)],text=True));new=decode((out/'tws-shutdown-candidate.disassembly.txt').read_text());cases=0
    for seed in (0,1,0x7fffffff,0x80000000,0xffffffff,0x12345678):
        for result in (*range(256),0x7fffffff,0x80000000,0xffffffff):
            for kind,offset in [('buffer',0x11bd0),('done',0x11bd8)]:
                wanted=expected(kind,result)
                for code,pc,delta in ((old,offset,DELTA),(new,offset+DELTA,0)):
                    trace,ret=execute(code,pc,delta,seed,result)
                    if (trace,ret if kind=='buffer' else None)!=wanted:raise ValueError('TWS lifecycle helper contract mismatch')
                cases+=1
    rows=[]
    for region in evidence['regions']:
        is_data=region['section_name']=='.message'
        if not region['fits'] or not region['exact_stock_payload']:raise ValueError('TWS lifecycle region validation')
        rows.append({'symbol':region['symbol'],'section_name':region['section_name'],'ownership_kind':'generated_source_data' if is_data else 'compiled_c','compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':region['symbol'],'package_offset':region['package_offset'],'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-TWS-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'tws-shutdown-candidate.elf',output/'tws-shutdown.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':4,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,'limits':['Wrapper-level call/return qualification only. memset and printf have separate source qualification; audio/recognition shutdown and buffer initialization remain retained and are represented by their call contracts. No whole-TWS or hardware execution qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-tws-shutdown-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
