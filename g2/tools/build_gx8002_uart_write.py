# SPDX-License-Identifier: MIT
"""Build the recovered UART blocking buffer write with the native macOS toolchain."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_write.c'
    out=ROOT/'build/gx8002-uart-write';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'control.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Write stock identity')
    script=out/'write.ld'
    script.write_text('SECTIONS { .text 0x10203604 : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_uart_transmit = 0x1020324c;\n')
    target=out/'write.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
    if any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('Write relocation')
    (out/'write.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[0xcb90:0xcbbc]),'package_offset':0xcb90,'envelope_bytes':44,'fits':len(data)<=44,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-write-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
