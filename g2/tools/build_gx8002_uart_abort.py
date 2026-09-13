# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_abort.c'
    out=ROOT/'build/gx8002-uart-abort';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'control.o'
    subprocess.run([pre+'gcc','-Os','-fno-shrink-wrap',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('UART abort stock identity')
    rows=[]
    for kind,offset,size in (('transmit_abort_dma',0xc7a8,24),('receive_abort_dma',0xc7c0,24),('transmit_abort',0xcc74,28),('receive_abort',0xcc90,28)):
        symbol='open_cfw_gx8002_uart_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_dma_abort = 0x10203b40;\nopen_cfw_gx8002_uart_transmit_abort_dma = 0x1020321c;\nopen_cfw_gx8002_uart_receive_abort_dma = 0x10203234;\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('UART abort relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. Signed channel gating, abort call order, mode gating and descriptor reset need decoded qualification.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-abort-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
