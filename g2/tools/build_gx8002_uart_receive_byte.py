# SPDX-License-Identifier: MIT
"""Build the recovered UART blocking byte receive with the native macOS toolchain."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_receive_byte.c'
    out=ROOT/'build/gx8002-uart-receive-byte';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'control.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Receive byte stock identity')
    script=out/'receive_byte.ld'
    script.write_text('SECTIONS { .text 0x10203260 : { *(.text*) } }\n')
    target=out/'receive_byte.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
    if any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('Receive byte relocation')
    (out/'receive_byte.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[0xc7ec:0xc804]),'package_offset':0xc7ec,'envelope_bytes':24,'fits':len(data)<=24,'source_admitted':False,'hardware_qualified':False}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-receive-byte-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
