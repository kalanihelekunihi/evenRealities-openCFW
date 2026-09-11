#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Clock-boundary decoded composition; gate lookup and nested stack abstracted."""
import json,struct,subprocess
from itertools import product
import compare_gx8002_platform_gate as gate
from verify_gx8002_rtc_init import ROOT,build,decode,execute,expected
from verify_gx8002_padmux_get import build as build_getter,programs


def verify():
    candidate=build();build_getter();programs();placement=gate.link()
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    out=ROOT/'build/gx8002-board';gout=ROOT/'build/gx8002-platform-gate'
    stock=gate.IMAGE.read_bytes();table=stock[0x186f4:0x18894]
    wrapper=gout/'rtc-composition-stock.elf'
    subprocess.run([prefix+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(gate.IMAGE),str(wrapper)],check=True)
    wrapped=bytearray(wrapper.read_bytes());struct.pack_into('<I',wrapped,36,0x21006009);wrapper.write_bytes(wrapped)
    old_gate=decode(subprocess.check_output([prefix+'objdump','-D','--start-address=0x17094','--stop-address=0x17194',str(wrapper)],text=True))
    new_gate=decode(subprocess.check_output([prefix+'objdump','-d',str(gout/'gate-fit.elf')],text=True))
    elf=gate.Elf32((gout/'gate-fit.elf').read_bytes(),'gate-fit')
    jumps=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_platform_gate'))
    old=decode(subprocess.check_output([prefix+'objdump','-D','--start-address=0xfc48','--stop-address=0xfc90',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'rtc-init-candidate.disassembly.txt').read_text())
    count=calls=0
    traces=[]
    for outer,helper,frequency,register in product((0,1),(0,1),(0,32768,65535,65536,0xffffffff),(0,0xffffffff,0x55555555)):
        observed=[]
        def hook(module,enable):
            nonlocal calls
            if (module,enable)!=(0,1): raise ValueError('Unexpected RTC gate request')
            trace=gate.execute(new_gate if helper else old_gate,0x10025080 if helper else 0x17094,
                               jumps if helper else stock[0x173e0:0x17474],table,module,enable,register,
                               0 if helper else 0x1000dfec)
            if trace!=gate.oracle(table,module,enable,register): raise ValueError('Composed gate mismatch')
            for item in trace:
                if item[0]=='write' and item[1] not in (0xa001001c,0xa0010020,0xa030001c,0xa0300020):
                    raise ValueError('Gate writes outside clock controls')
            observed.append((module,enable,trace));calls+=1
        result=execute(new if outer else old,0x102066bc if outer else 0xfc48,frequency,0x12345678,gate_hook=hook)
        if result!=expected(frequency,0x12345678):raise ValueError('RTC init trace mismatch')
        if [x[:2] for x in observed]!=[(0,1)]: raise ValueError('Missing gate boundary')
        if count<3: traces.append(observed)
        count+=1
    return {'candidate':candidate,'gate_placement':placement,'combinations':count,'decoded_gate_calls':calls,
            'sample_gate_traces':json.loads(json.dumps(traces)),'source_admitted':False,'hardware_qualified':False,
            'limits':['Call-boundary composition only: helper executes with its own abstract stack and modeled lookup/table. RTC caller clobbers modeled; frequency/IRQ/printf/start helpers remain modeled. No nested stack sharing, concurrent changes, or physical clock effects proved.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-rtc-init-gate-composition.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Combinations:',report['combinations'],'gate calls:',report['decoded_gate_calls'])
