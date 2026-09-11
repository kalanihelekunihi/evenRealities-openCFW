# SPDX-License-Identifier: MIT
"""Qualify arithmetic in isolated oversized frequency probe, not firmware."""
import json
import subprocess
from itertools import product
from probe_gx8002_clock_frequency_size import probe, ROOT
from link_gx8002_clock_frequency_candidate import link, Elf32, sha
from verify_gx8002_clock_pll_slice import execute as pll, frequency, decode
from verify_gx8002_clock_dto_slice import execute as dto, expected, MASK
from verify_gx8002_clock_selection import execute as selection, expected as selection_expected
from verify_gx8002_frequency_dispatch import execute as dispatch, expected as dispatch_expected


def verify():
    link()
    evidence=probe()
    out=ROOT/'build/gx8002-clock-frequency-size-probe'
    script=out/'analysis.ld'
    script.write_text((ROOT/'build/gx8002-clock-frequency/frequency-analysis.ld').read_text())
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(script),str(out/'frequency.o'),'-o',str(out/'analysis.elf')],check=True)
    assembly=subprocess.check_output([pre+'objdump','-d',str(out/'analysis.elf')],text=True)
    (out/'analysis.disassembly.txt').write_text(assembly)
    code=decode(assembly)
    elf=Elf32((out/'analysis.elf').read_bytes(), 'frequency size probe')
    table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency'))
    ndispatch=0
    for module in (*range(256),0x7fffffff,0x80000000,0xffffffff):
        if dispatch(code,0x10025210,module,table,0x11000000,0)!=dispatch_expected(module):
            raise ValueError('Probe dispatch mismatch')
        ndispatch+=1
    scases=0
    for module, offset, source, bits in product(range(26), (0,4,15,30), (0,1,1<<18,(1<<18)|1), product(range(4),repeat=3)):
        values=tuple(b<<offset for b in bits)
        result=selection(code,True,module,offset,source,values,
                         {0x10025246:'return',0x100252a6:'divider',0x100252ec:'pll',0x10025380:'dto'})
        if result!=selection_expected(module,offset,source,values):
            raise ValueError('Probe selection mismatch')
        scases+=1
    pcases=dcases=0
    for words in product((0,1,31,63),(0,59,95,255,2047),(0,1,31),(0,7),(0,16,32,48)):
        reads,result=pll(code,0x100252ec,(0x10025380,0x10025246),words)
        if result!=frequency(*words) or [a for a,v in reads]!=[0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030]:
            raise ValueError('Probe PLL mismatch')
        pcases+=1
    for args in product((False,True),(0,1,0x1ffffff,0x8000000,0x9ffffff,MASK),(0,1,32000,24576000,98304000,MASK)):
        if dto(code,0x10025380,0x100252a6,*args)!=expected(*args):
            raise ValueError('Probe DTO mismatch')
        dcases+=1
    return {'candidate':evidence,'analysis_elf_sha256':sha((out/'analysis.elf').read_bytes()),'dispatch_cases':ndispatch,'selection_cases':scases,'pll_cases':pcases,'dto_cases':dcases,'source_admitted':False,
            'limits':['Selection and arithmetic slices only; oversized candidate, no full ABI, lookup or hardware qualification.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-clock-size-probe-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)
