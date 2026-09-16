# SPDX-License-Identifier: MIT
"""Stage-one frequency comparison with explicit synthetic lookup descriptors."""
import json,struct,subprocess
from itertools import product
from build_gx8002_stage1_clock_frequency import build,ROOT,IMAGE,sha,IMAGE_SHA,Elf32
from execute_gx8002_backup_clock_frequency import execute
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x38c54','--stop-address=0x38e48',str(wrapper)],text=True))
    path=ROOT/'build/gx8002-stage1-clock-frequency/frequency.elf'
    new=decode(subprocess.check_output([tool,'-d',str(path)],text=True))
    elf=Elf32(path.read_bytes(),'frequency')
    tables=[struct.unpack_from('<19I',stock,0x39d0c),struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata')))]
    cases=0
    for module,result,offset,source,div in product((*range(28),0xffffffff),(0,1,0xffffffff),(0,3,255),(0,1<<18),(0,1,31)):
        cells={(0x20031006,1):offset,(0x20031008,4):0x20031200,(0x20031200,1):0x24,(0x20031201,1):0,(0x20031202,2):31,(0xa0300024,4):div,(0xa0010090,4):0}
        hook=lambda m:(result,[],[(0x1000,0x20031000),(0x1004,0xa0300000),(0x1008,0xa0010090)])
        args=dict(module=module,lookup_result=result,offset_byte=offset,source_word=source,source_cells=cells,lookup_hook=hook,lookup_entry=0x10000138,jump_base=0x100013b8)
        traces=[[],[]]
        a=execute(old,tables[0],entry=0x38c54,delta=0x10000000-0x38954,mmio_trace=traces[0],**args)
        b=execute(new,tables[1],entry=0x10000300,mmio_trace=traces[1],**args)
        assert a==b and traces[0]==traces[1],(module,result,offset,source,div,a,b,traces)
        hz=0 if module in (7,8) or result or offset==255 else (1024000 if source else 12288000)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if hz and mapped not in (2,6,9) and mapped<=9:hz=hz//(div+1) if div else hz
        assert b[0]==hz,(module,result,offset,source,div,b,hz)
        cases+=1
    report={'cases':cases,'build':evidence,'limits':['Low-frequency paths with synthetic descriptor lookup; finite stock/source traces and independent output oracle.', 'Actual descriptor lookup/table closure, high PLL and changing register paths, references, startup integration and hardware execution remain unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-clock-frequency-execution.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':print(verify()['cases'],'stage-one frequency cases passed')
