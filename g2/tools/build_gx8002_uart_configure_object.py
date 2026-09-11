# SPDX-License-Identifier: MIT
"""Native source compilation only; UART config behavior not yet qualified."""
import json,subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE,IMAGE_SHA
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    data=IMAGE.read_bytes()
    if sha(data)!=IMAGE_SHA:raise ValueError('Stock identity')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_configure.c'
    out=ROOT/'build/gx8002-uart-configure';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'configure.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    elf=Elf32(obj.read_bytes(),str(obj));text=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_uart_configure')
    (out/'configure.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-dr',str(obj)],text=True))
    runtime=Path(subprocess.check_output([pre+'gcc','-print-libgcc-file-name'],text=True).strip())
    if not runtime.is_file():raise ValueError('Native target libgcc unavailable')
    script=out/'runtime.ld'
    script.write_text('SECTIONS { .text 0x10320000 : { *(.text*) } .rodata : { *(.rodata*) } }\nopen_cfw_gx8002_uart_fifo_depth = 0x10203360;\nopen_cfw_gx8002_uart_interrupt = 0x10203278;\nopen_cfw_gx8002_request_irq = 0x1002553c;\n')
    linked=out/'runtime.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),str(runtime),'-o',str(linked)],check=True)
    target=Elf32(linked.read_bytes(),str(linked))
    undefined=[s['name'] for s in target.symbols() if s['name'] and s['section']==0]
    if undefined:raise ValueError(('Runtime unresolved',undefined))
    (out/'runtime.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))
    runtime_info={'archive':str(runtime),'archive_sha256':sha(runtime.read_bytes()),'linked_sha256':sha(linked.read_bytes()),'unresolved_symbols':undefined,'gcc_source_commit':subprocess.check_output(['git','-C',str(ROOT/'build/upstream-csky-toolchain-build/gcc'),'rev-parse','HEAD'],text=True).strip(),'hardware_qualified':False}
    return {'runtime_link':runtime_info,'source_sha256':sha(source.read_bytes()),'compiled_bytes':text['size'],'undefined_dependencies':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0],'stock_offset':0xc954,'stock_envelope_bytes':360,'stock_sha256':sha(data[0xc954:0xcabc]),'source_admitted':False,'limits':['Analysis link uses source-built libgcc; UART/IRQ dependencies remain absolute bindings. Full MMIO ordering and float conversion/helper correspondence require qualification. No linked firmware output. Baud values that overflow baud<<4 to zero remain outside a defined C division domain.']}

if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-uart-configure-object.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
