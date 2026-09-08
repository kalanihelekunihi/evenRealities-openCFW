#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Conservative nested-stack checks at every decoded wrapper boundary."""
import contextlib,io,json,subprocess
from verify_gx8002_irq_architecture_frame import verify as verify_architecture
from verify_gx8002_irq_software_frame import ROOT,decode,execute

def verify():
    with contextlib.redirect_stdout(io.StringIO()):architecture=verify_architecture()
    pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'
    code=decode(subprocess.check_output([str(pre),'-d',str(ROOT/'build/gx8002-irq/entry.elf')],text=True))
    boundaries=[];pc=0x10025574
    while True:
        boundaries.append(pc)
        op,args,width=code[pc]
        if op=='nir':break
        pc+=width
    rows=[]
    for boundary in boundaries:
     for depth in (1,2,3):
      peaks=[]
      for seed in (0,1,0xffffffff,0x55555555,0xaaaaaaaa,0x80000000):
        result=execute(code,0x10025574,seed,depth,architecture=True,interrupt_pc=boundary)
        if result['calls']!=1 or result['software_frame_bytes']!=100:raise ValueError('boundary frame result')
        peaks.append(result['modeled_peak_bytes'])
      if len(set(peaks))!=1:raise ValueError('data-dependent frame size')
      rows.append({'boundary':boundary,'instruction':code[boundary][0],'nested_depth':depth,'peak_bytes':peaks[0]})
    report={'architecture_evidence':architecture,'cases':len(rows)*6,'boundaries':len(boundaries),'results':rows,
            'source_admitted':False,'limits':['Injects at every wrapper instruction boundary regardless of actual PSR eligibility. This checks stack/register preservation under that conservative schedule, not instruction atomicity, exception acceptance timing, callback capacity or hardware behavior.']}
    (ROOT/'docs/research/gx8002-irq-boundary-nesting-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cases']);return report
if __name__=='__main__':verify()
