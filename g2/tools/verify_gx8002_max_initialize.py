#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify MAX count check and owned strategy-init call using decoded code."""
import json,re,shutil,struct,subprocess
from build_gx8002_max_initialize_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import sha
MASK=0xffffffff
DELTA=0x101f6a74

def execute(code,pc,delta,count,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;trace=[];condition=False
    for _ in range(20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('MAX frame')
            saved=r['r15'];r['r14']-=4
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('MAX load operand')
            dst,base,off=m.groups();address=(r[base]+int(off,0))&MASK
            if address!=0x2002e79c:raise ValueError('MAX count address')
            trace.append(['read',address,count]);r[dst]=count
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('MAX call frame')
            target=(int(args,0)+delta)&MASK
            if target==0x10206c24:
                if r['r0']!=0x1020b30d:raise ValueError('MAX diagnostic')
                trace.append(['printf',r['r0']])
            elif target==0x10208978:trace.append(['KwsStrategyInit'])
            else:raise ValueError('MAX unknown helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
        elif op=='pop':
            if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('MAX return frame')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('MAX ABI')
            return trace
        else:raise ValueError('unknown MAX instruction '+op)
        pc=nxt
    raise ValueError('MAX execution bound')

def expected(count):return [['read',0x2002e79c,count]]+([['printf',0x1020b30d]] if count!=2 else [])+[['KwsStrategyInit']]

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'max-initialize-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11ed0','--stop-address=0x11ef0',str(w)],text=True));new=decode((out/'max-initialize-candidate.disassembly.txt').read_text());cases=0
    for count in (*range(256),0x7fffffff,0x80000000,0xffffffff,*[1<<i for i in range(8,31)]):
     for seed in (0,0xffffffff,0x12345678):
      for code,pc,delta in ((old,0x11ed0,DELTA),(new,0x10208944,0)):
       if execute(code,pc,delta,count,seed)!=expected(count):raise ValueError('MAX call trace')
      cases+=1
    rows=[]
    for region in evidence['regions']:
        is_data=region['section_name']=='.rodata.message'
        if not region['fits'] or (is_data and not region['exact_stock_payload']):raise ValueError('MAX region validation')
        symbol='open_cfw_gx8002_max_init_error' if is_data else 'LvpInitMaxKws'
        rows.append({'symbol':symbol,'section_name':region['section_name'],'ownership_kind':'generated_source_data' if is_data else 'compiled_c',
        'compiled_bytes':region['compiled_bytes'],'compiled_sha256':region['compiled_sha256'],'stock_occurrences':[{'symbol':symbol,'package_offset':region['package_offset'],
        'bytes':region['stock_envelope_bytes'],'sha256':region['stock_sha256'],'region':'image_a_xip_text'}]})
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-MAX-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'max-initialize-candidate.elf',output/'max-initialize.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':rows,'evidence':evidence,'cases':cases,'frame_bytes':4,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
      'limits':['MAX initializer and diagnostic only. printf and strategy init/reset have independent source qualification. Keyword list state and complete scoring/strategy remain separate; no whole-decoder or hardware qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-max-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
