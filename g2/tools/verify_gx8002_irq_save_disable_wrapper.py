# SPDX-License-Identifier: MIT
"""Verify wrapper target and composed saved-bank/disable effects."""
import json,subprocess
from itertools import product
from build_gx8002_irq_save_disable_wrapper import build,ROOT,sha,Elf32
from compare_gx8002_irq import execute
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');p=ROOT/'build/gx8002-irq-save-disable-wrapper/wrapper.elf';wrapper=decode(subprocess.check_output([pre,'-d',str(p)],text=True))
    p=ROOT/'build/gx8002-source-candidate/irq/irq.elf';elf=Elf32(p.read_bytes(),'irq');report=json.loads((ROOT/'docs/research/gx8002-irq-verification.json').read_text())
    for row in report['functions']:
        s=next(s for s in elf.sections if s['name']==row.get('section_name','.text.'+row['symbol']));assert sha(elf.contents(s))==row['compiled_sha256']
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};assert symbols['open_cfw_gx8002_irq_save_disable']==0x1002550c and symbols['open_cfw_gx8002_irq_disable']==0x100254c8
    code=decode(subprocess.check_output([pre,'-d',str(p)],text=True));cases=0
    for a,b in product((0,1,0x80000000,0xffffffff,0x55555555),(0,1,0x80000000,0xffffffff,0xaaaaaaaa)):
        # Wrapper preserves ABI and forwards once; expand its call with decoded callee.
        assert execute(wrapper,0x10025534,0,enable=0x1002550c,call_name='save_disable')==[('save_disable',0)]
        trace=execute(code,0x1002550c,0,enable=0x100254c8,memory={0xe000e100:a,0xe000e104:b},call_name='disable')
        expanded=[]
        for event in trace:
            if event[0]=='disable':expanded.extend(execute(code,0x100254c8,event[1]))
            else:expanded.append(event)
        expected=[('read',0xe000e100,a),(0x20026eec,a),('read',0xe000e104,b),(0x20026ef0,b)]+[(0xe000e180,1<<i) for i in range(32)]
        assert expanded==expected;cases+=1
    return {'candidate':candidate,'callee_elf_sha256':sha(p.read_bytes()),'cases':cases,'disable_executions':cases*32,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded wrapper forwards once to authenticated source callee; callee and32 disable bodies execute in separate frames with independent saved-bank/VIC-write oracle.','No shared physical stack or concurrent register mutation modeled; original public wrapper name unresolved. Registry admission pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-irq-save-disable-wrapper-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('IRQ wrapper cases:',r['cases'])
