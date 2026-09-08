#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check compact entry at each instruction boundary, under a conservative schedule."""
import contextlib,io,json
from verify_gx8002_irq_compact import verify as verify_base,execute,ROOT,decode

def verify():
    with contextlib.redirect_stdout(io.StringIO()):base=verify_base()
    code=decode((ROOT/'build/gx8002-irq/compact.disassembly.txt').read_text())
    boundaries=[];pc=0x10025574
    while True:
        boundaries.append(pc);op,args,width=code[pc]
        if op=='nir':break
        pc+=width
    rows=[];cases=0
    for boundary in boundaries[1:]:
     for depth in (1,2,3):
      peaks=[]
      for seed in (0,0xffffffff,0x12345678):
        result=execute(code,63,0x10026000,0x20028000,seed,depth,boundary)
        plain=execute(code,63,0x10026000,0x20028000,seed)
        if result['trace']!=plain['trace'] or not 124<=result['peak_bytes']<=124*(depth+1):raise ValueError('nested effects/frame')
        peaks.append(result['peak_bytes']);cases+=1
      if len(set(peaks))!=1:raise ValueError('seed-dependent stack usage')
      rows.append({'boundary':boundary,'instruction':code[boundary][0],'nested_depth':depth,'peak_bytes':peaks[0]})
    report={'base':base,'cases':cases,'boundaries':len(boundaries)-1,'results':rows,'source_admitted':False,
            'limits':['Only post-NIE boundaries tested; nested entry overwrites outer EPC/EPSR. Nested register values inherited and stack shared; callbacks obey C ABI. Boundary injection over-approximates actual IE/priority acceptance and excludes instruction-internal faults. No physical capacity or callback stack bound is claimed.']}
    (ROOT/'docs/research/gx8002-irq-compact-nesting-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
