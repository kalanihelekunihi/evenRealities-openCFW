#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Track documented NIE/NIR enable-bit effects over the decoded wrapper.

IE permits interrupts but does not imply controller acceptance or priority.
Callback PSR values are explicit assumptions, not a callback implementation.
"""
import contextlib,io,json,re,subprocess
from verify_gx8002_irq_architecture_frame import verify as verify_architecture
from verify_gx8002_irq_software_frame import ROOT,decode
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob

IE=1<<6;EE=1<<8

def transitions(code,entry_psr,saved_epsr,callback_psr):
    psr=entry_psr;pc=0x10025574;rows=[];entered=False;called=False
    for _ in range(20):
        op,args,width=code[pc]
        rows.append({'pc':pc,'instruction':op,'psr':psr,'ie_set':bool(psr&IE),'ee_set':bool(psr&EE)})
        if op=='nie':
            if entered:raise ValueError('duplicate NIE')
            entered=True;psr|=IE|EE
        elif op=='bsr':
            if not entered or called or int(args,0)!=0x10025598:raise ValueError('dispatch order')
            called=True;psr=callback_psr
        elif op=='nir':
            if not entered or not called:raise ValueError('return order')
            return rows,saved_epsr
        elif op not in ('ipush','ipop','subi','addi','stm','ldm','fstms','fldms'):
            raise ValueError('unreviewed PSR effect')
        pc+=width
    raise ValueError('missing NIR')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):architecture=verify_architecture()
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';relative='arch/soc/grus/include/core_ck804.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+relative],text=True).strip()
    header=authenticated_blob(sdk/relative,blob).decode()
    for name,value in (('IE',6),('EE',8)):
        if not re.search(r'#define PSR_'+name+r'_Pos\s+'+str(value)+r'U\b',header):raise ValueError('PSR position changed')
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(ROOT/'build/gx8002-irq/entry.elf')],text=True))
    cases=0;examples=[]
    for entry in (0,IE,IE|EE,0xffffffff):
     for saved in (0,IE,IE|EE,0x80000000,0xffffffff):
      for callback in (0,IE,IE|EE,0x80000000,0xffffffff):
        rows,result=transitions(code,entry,saved,callback)
        if result!=saved:raise ValueError('NIR does not restore full PSR')
        after_call=False
        for i,row in enumerate(rows):
            expected=entry if i==0 else callback if after_call else entry|IE|EE
            if row['psr']!=expected:raise ValueError('PSR trace mismatch')
            if row['instruction']=='bsr':after_call=True
        if entry==0 and saved==0:examples.append({'callback_psr':callback,'boundaries':rows,'return_psr':result})
        cases+=1
    report={'architecture_evidence':architecture,'sdk_header_git_blob':blob,'cases':cases,'examples':examples,
            'source_admitted':False,'limits':['NIE/NIR effects follow the pinned ISA and SDK bit positions. Callback PSR is supplied parametrically. IE-set boundaries are not proof of priority acceptance, exception timing, atomic stack accesses or available stack capacity. Handler-entry PSR and saved EPSR are inputs, not assertions about exception-entry hardware.']}
    (ROOT/'docs/research/gx8002-irq-enable-state-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
