# SPDX-License-Identifier: MIT
"""Build the recovered UART drain wait with the native macOS toolchain."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build(prefix=None,output=None):
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_flush.c'
    out=output or ROOT/'build/gx8002-uart-flush';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-' if prefix is None else prefix/'csky-unknown-elf-')
    obj=out/'control.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Flush stock identity')
    script=out/'flush.ld'
    script.write_text('SECTIONS { .text 0x10203598 : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\n')
    target=out/'flush.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
    if any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('Flush relocation')
    (out/'flush.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[0xcb24:0xcb40]),'package_offset':0xcb24,'envelope_bytes':28,'fits':len(data)<=28,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-flush-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
