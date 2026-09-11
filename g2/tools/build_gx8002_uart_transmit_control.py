# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_transmit_control.c'
    out=ROOT/'build/gx8002-uart-transmit-control';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'control.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Transmit control stock identity')
    rows=[]
    for kind,offset,size in (('start',0xcbbc,52),('stop',0xcbf0,40)):
        symbol='open_cfw_gx8002_uart_transmit_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('Transmit control relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. IRQ return-token preservation, descriptor writes and MMIO transaction order need decoded qualification.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-transmit-control-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
