# SPDX-License-Identifier: MIT
"""Execute compiled upstream fill against an independent byte-array oracle."""
import json
from build_gx8002_beam_fill_q15 import build,ROOT
from execute_gx8002_imcra_process import execute
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();code=decode((ROOT/'build/gx8002-beam-fill-q15/fill.disassembly.txt').read_text())
    cases=0
    for count in (0,1,2,3,4,5,7,16,63,256,512):
      for value in (0,1,32767,32768,65535):
       for offset in (0,2):
        base=0x21000000;address=base+8+offset
        memory={base+i:0xa5 for i in range(1056)}
        expected=dict(memory)
        for i in range(count):
            expected[address+2*i]=value&255;expected[address+2*i+1]=value>>8
        result=execute(code,0x1000f1ac,memory,[value,address,count],{})
        assert result['memory']==expected,(count,value,offset)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Compiled upstream fill executed with saved-register checks against byte-array oracle and surrounding sentinels.','Not decoded stock packed-instruction equivalence, MMIO qualification, or startup integration.']}
    (ROOT/'docs/research/gx8002-beam-fill-q15-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
