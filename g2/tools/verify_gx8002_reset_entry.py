#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify reset effects and original returned-main loop from decoded source."""
import contextlib,io,json,shutil
from build_gx8002_reset_candidate import build,ROOT
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_logging import check_paths
from verify_gx8002_memcpy_source import decode

def execute(code,control,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};pc=0x10023500;trace=[]
    for _ in range(24):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mtcr':
            reg,cr=args.split(', ',1)
            if cr not in ('cr<0, 0>','cr<31, 0>'):raise ValueError('control destination')
            trace.append(['control-write',cr,r[reg]])
        elif op=='mfcr':
            if args!='r1, cr<31, 0>':raise ValueError('control source')
            r['r1']=control;trace.append(['control-read','cr<31, 0>',control])
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bsr':
            target=int(args,0)
            if target not in (0x1002354c,0x10026314):raise ValueError('unknown reset call')
            if r['r14']!=0x2002f7fc:raise ValueError('reset stack')
            trace.append(['call',target,r['r14']])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&0xffffffff
        elif op=='br':
            if int(args,0)!=pc:raise ValueError('returned-main loop')
            trace.append(['returned-main-loop',pc]);return trace
        else:raise ValueError('unknown reset instruction')
        pc+=width
    raise ValueError('reset bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    if not evidence['byte_exact']:raise ValueError('reset bytes changed')
    code=decode((ROOT/'build/gx8002-board/reset-entry.disassembly.txt').read_text());cases=0
    for control in sorted({0,0xffffffff,0x55555555,0xaaaaaaaa,*(1<<i for i in range(32))}):
     for seed in (0,0xffffffff,0x12345678):
      expected=[['control-write','cr<0, 0>',0x80000200],['control-read','cr<31, 0>',control],
        ['control-write','cr<31, 0>',control&~8],['call',0x1002354c,0x2002f7fc],
        ['call',0x10026314,0x2002f7fc],['returned-main-loop',0x1002351c]]
      if execute(code,control,seed)!=expected:raise ValueError('reset effects')
      cases+=1
    notice=ROOT/'components/shared/gx8002/NATIONALCHIP-STARTUP-NOTICE.txt'
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/reset-entry.elf',output/'reset-entry.elf');shutil.copyfile(notice,output/notice.name)
    return {'functions':[{'symbol':'open_cfw_gx8002_reset_entry','section_name':'.text','ownership_kind':'compiled_assembly',
        'compiled_bytes':40,'compiled_sha256':evidence['compiled_sha256'],'stock_occurrences':[{
        'symbol':'open_cfw_gx8002_reset_entry','package_offset':0x15514,'bytes':40,
        'sha256':evidence['compiled_sha256'],'region':'image_a_sram_text'}]}],
        'evidence':evidence,'cases':cases,'notice_sha256':sha(notice.read_bytes()),'source_admitted':True,'hardware_qualified':False,
        'limits':['Reset architecture assembly derived from pinned MIT upstream. Main and full startup composition remain separate; returned-main loop is original behavior, not a substitute for main. No physical boot qualification.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-reset-entry-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
