# SPDX-License-Identifier: MIT
"""Link and qualify UART configuration at its stock address on native macOS."""
import json,subprocess
from pathlib import Path
from build_gx8002_uart_configure_object import build,ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_uart_configure import verify as core
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build()
    output=Path(output) if output else ROOT/'build/gx8002-uart-configure-source'
    output.mkdir(parents=True,exist_ok=True)
    offsets={'__floatunsidf':0x13a5c,'__divdf3':0x13894,'__muldf3':0x13694,'__adddf3':0x13628,'__fixunsdfsi':0x12ff8,
        'open_cfw_gx8002_uart_fifo_depth':0xc8ec,'open_cfw_gx8002_uart_interrupt':0xc804}
    bindings={name:offset+0x101f6a74 for name,offset in offsets.items()}
    bindings['open_cfw_gx8002_request_irq']=0x1002553c
    script=output/'configure.ld'
    script.write_text('SECTIONS { .text 0x102033c8 : { *(.text*) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');target=output/'configure.elf'
    subprocess.run([pre+'ld','-T',str(script),str(ROOT/'build/gx8002-uart-configure/configure.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    if len(data)>candidate['stock_envelope_bytes'] or any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('UART configuration replacement extent/relocation')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('UART configuration unresolved symbol')
    disassembly=output/'configure.disassembly.txt';disassembly.write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    names=dict(uint='__floatunsidf',divide='__divdf3',multiply='__muldf3',add='__adddf3',fix='__fixunsdfsi',fifo='open_cfw_gx8002_uart_fifo_depth',irq='open_cfw_gx8002_request_irq')
    qualification=core(True,True,(disassembly,0x102033c8,{bindings[name]:kind for kind,name in names.items()}))
    if qualification['candidate']!=candidate:raise ValueError('UART configuration candidate drift')
    symbol='open_cfw_gx8002_uart_configure'
    row={'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'section_name':'.text',
        'stock_occurrences':[{'symbol':symbol,'package_offset':candidate['stock_offset'],'bytes':candidate['stock_envelope_bytes'],'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}
    evidence=('verify_gx8002_uart_configure_source.py','build_gx8002_uart_configure_object.py','verify_gx8002_uart_configure.py','execute_gx8002_uart_configure.py','verify_gx8002_memcpy_source.py',
        'verify_gx8002_uint_double_prepare.py','execute_gx8002_double_multiply.py','execute_gx8002_double_subtract_prepare.py','execute_gx8002_double_fix_tail.py','execute_gx8002_double_ge.py','verify_gx8002_double_uint_wrapper.py','verify_gx8002_uart_fifo_depth.py','execute_gx8002_linked_irq_registration.py')
    return {'functions':[row],'bindings':bindings,'qualification':qualification,
        'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Exact replacement-address configuration executes with decoded source-built arithmetic, FIFO and IRQ-registration helpers in separate frames. Modeled peripheral stimuli and finite numeric corpus; baud values whose shifted denominator is zero are outside qualification. Hardware and full firmware execution remain unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-configure-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('UART configuration source admission:',r['qualification']['cases'])
