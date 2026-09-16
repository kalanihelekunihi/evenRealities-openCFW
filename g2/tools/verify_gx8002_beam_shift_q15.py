# SPDX-License-Identifier: MIT
"""Compiled scalar shift versus integer saturation oracle; not stock equivalence."""
import json
from build_gx8002_beam_shift_q15 import build,ROOT
from execute_gx8002_imcra_process import execute
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();code=decode((ROOT/'build/gx8002-beam-shift-q15/shift.disassembly.txt').read_text());cases=0
    values=(-32768,-32767,-16384,-129,-1,0,1,127,16384,32766,32767)
    for shift in range(-128,128):
      for count in (0,1,len(values)):
       for inplace in (False,True):
        base=0x21000000;src=base+8;dst=src if inplace else base+64
        memory={base+i:0xa5 for i in range(128)}
        for i,v in enumerate(values):
            memory[src+2*i]=v&255;memory[src+2*i+1]=(v>>8)&255
        expected=dict(memory)
        for i,v in enumerate(values[:count]):
            result=max(-32768,min(32767,v*(1<<shift))) if shift>=0 else v//(1<<((-shift)&31))
            expected[dst+2*i]=result&255;expected[dst+2*i+1]=(result>>8)&255
        actual=execute(code,0x1000f0c0,memory,[src,shift,dst,count],{})
        assert actual['memory']==expected,(shift,count,inplace)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Compiled source checked against integer arithmetic oracle for shifts -128..127, disjoint/in-place buffers and selected samples.','No decoded packed-stock comparison, partial overlap, hardware or placement qualification. Candidate fits original envelope; integration remains pending.']}
    (ROOT/'docs/research/gx8002-beam-shift-q15-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
