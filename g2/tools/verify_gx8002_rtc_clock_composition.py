# SPDX-License-Identifier: MIT
"""RTC init frequency call uses decoded candidate clock/lookup/divider."""
import json
import struct
import subprocess
from itertools import product
from verify_gx8002_rtc_init import execute,expected,ROOT,build,decode
from verify_gx8002_clock_low_frame import execute as clock
from build_transparent_image import Elf32


def verify():
    candidate=build();out=ROOT/'build/gx8002-board'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfc48','--stop-address=0xfc90',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'rtc-init-candidate.disassembly.txt').read_text())
    location=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((location/'placement.disassembly.txt').read_text());code.update(decode((out/'clock-divider-candidate.disassembly.txt').read_text()))
    elf=Elf32((location/'placement.elf').read_bytes(),'RTC clock composition');sections={s['name']:s for s in elf.sections}
    table=struct.unpack('<19I',elf.contents(sections['.rodata.open_cfw_gx8002_clock_frequency']))
    records=elf.contents(sections['.data.gx_clock_param_table']);divs=elf.contents(sections['.data.gx_clock_div_table']);cells={}
    for i in range(26):
        for off in (8,12):cells[0x200266e0+i*16+off,4]=struct.unpack_from('<I',records,i*16+off)[0]
    for i in range(17):
        addr=0x20026884+i*4;off,shift,mask=struct.unpack_from('<BBH',divs,i*4)
        cells[addr,1]=off;cells[addr+1,1]=shift;cells[addr+2,2]=mask
        for base in (0xa0010000,0xa0300000):cells[base+off,4]=0
    count=0
    for use_source,selector,control in product((False,True),(0,4,2),(0,0xffffffff)):
        state=cells.copy();state[0xa001008c,4]=selector;state[0xa0300088,4]=0
        calls=[]
        def hook(module):
            if module!=0:raise ValueError('RTC clock module')
            result,trace=clock(code,table,module,0,0,lookup_records=records,source_cells=state)
            calls.append(result);return result
        trace=execute(new if use_source else old,0x102066bc if use_source else 0xfc48,0,control,frequency_hook=hook)
        hz={0:12288000,4:32000,2:24576000}[selector]
        if calls!=[hz] or trace!=expected(hz,control):raise ValueError('RTC clock composition mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,
            'limits':['RTC and clock use separate frames; gate/IRQ/printf/start helpers remain modeled here. Existing clock ELF inputs; no hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-rtc-clock-composition.json').write_text(json.dumps(report,indent=2)+'\n');print('RTC/clock cases:',report['decoded_cases'])
