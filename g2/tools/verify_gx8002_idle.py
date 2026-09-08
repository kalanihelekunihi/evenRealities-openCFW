#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify original IDLE behaviors and source-authored callback object/messages."""
import json, shutil, subprocess, struct
from build_gx8002_idle_candidate import ROOT, IMAGE, CODE, DATA, PRINTF, DELTA, build
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
def execute(code,pc,delta,kind,argument,seed,printf_result):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=argument;r['r14']=0x2002f7fc
    initial=r.copy();saved=None;trace=[]
    for _ in range(12):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if saved is not None or args!='r15':raise ValueError('idle frame')
            saved=r['r15'];r['r14']-=4
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-4:raise ValueError('idle call frame')
            if (int(args,0)+delta)&MASK!=PRINTF:raise ValueError('idle helper')
            address=0x1020b1d8 if kind=='done' else 0x1020b1ee
            if r['r0']!=address or kind not in ('init','done'):raise ValueError('idle message')
            trace.append(['printf',address])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            r['r0']=printf_result
        elif op in ('pop','rts'):
            if op=='pop':
                if saved is None or args!='r15' or r['r14']!=initial['r14']-4:raise ValueError('idle return frame')
                r['r15']=saved;r['r14']+=4
            elif saved is not None:raise ValueError('idle outstanding frame')
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('idle ABI')
            return {'trace':trace,'result':r['r0'] if kind in ('init','buffer_init') else None}
        else:raise ValueError('unknown idle instruction '+op)
        pc+=width
    raise ValueError('idle execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    artifact=out/'idle-candidate.elf';elf=Elf32(artifact.read_bytes(),str(artifact));stock=IMAGE.read_bytes()
    functions=[]
    for row in evidence['functions']:
        sec=next(s for s in elf.sections if s['name']==row['section_name']);payload=elf.contents(sec);o=row['package_offset']
        if not row['fits'] or payload!=stock[o:o+len(payload)]:raise ValueError('idle executable/data identity')
        functions.append({'symbol':row['symbol'],'section_name':row['section_name'],'ownership_kind':row['ownership_kind'],
          'compiled_bytes':len(payload),'compiled_sha256':row['compiled_sha256'],'stock_occurrences':[{'symbol':row['symbol'],
          'package_offset':o,'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'image_a_xip_text'}]})
    w=out/'idle-stock.elf';subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11ba8','--stop-address=0x11bd0',str(w)],text=True))
    new=decode((out/'idle-candidate.disassembly.txt').read_text());cases=0
    for symbol,address,_ in CODE:
     kind=symbol.removeprefix('open_cfw_gx8002_idle_')
     expected={'trace':[['printf',0x1020b1d8 if kind=='done' else 0x1020b1ee]] if kind in ('done','init') else [],'result':0 if kind in ('init','buffer_init') else None}
     for argument in (0,1,2,0xffff,0x7fffffff,0x80000000,0xffffffff):
      for seed in (0,0xffffffff,0x12345678):
       for result in (0,1,0x80000000,0xffffffff):
        for code,entry,delta in ((old,address-DELTA,DELTA),(new,address,0)):
         if execute(code,entry,delta,kind,argument,seed,result)!=expected:raise ValueError('idle behavior')
        cases+=1
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-IDLE-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(artifact,output/'idle.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':functions,'evidence':evidence,'cases':cases,'notice_sha256':sha(notice.read_bytes()),
            'source_admitted':True,'hardware_qualified':False,'limits':['IDLE callbacks and their typed object/messages only. Empty tick and zero-return buffer init are original behavior. printf already has independent source qualification; no TWS/system or whole-device qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-idle-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
