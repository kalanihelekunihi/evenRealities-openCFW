# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_transmit_dma.c'
    out=ROOT/'build/gx8002-uart-transmit-dma-placement';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'control.o'
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
    header='include/driver/gx_dma_ahb.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,blob)
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    entry_source=out/'entry.S'
    entry_source.write_text('.section .text.entry,"ax"\n.global open_cfw_gx8002_uart_transmit_dma_entry\nopen_cfw_gx8002_uart_transmit_dma_entry:\n br open_cfw_gx8002_uart_transmit_dma\n')
    subprocess.run([pre+'gcc','-mcpu=ck804ef','-mhard-float','-c',str(entry_source),'-o',str(out/'entry.o')],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Transmit DMA stock identity')
    rows=[]
    for kind,offset,size in (('dma',0x13200,144),):
        symbol='open_cfw_gx8002_uart_transmit_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .entry 0x10203108 : { *(.text.entry) } .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_transmit_complete = 0x102030c4;\nopen_cfw_gx8002_dcache_clean_range = 0x10025664;\nopen_cfw_gx8002_dma_release = 0x10203b38;\nopen_cfw_gx8002_dma_select = 0x10203a4c;\nopen_cfw_gx8002_uart_dma_burst = 0x10203050;\nopen_cfw_gx8002_dma_callback = 0x10203b64;\nopen_cfw_gx8002_dma_transfer = 0x10203b78;\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),str(out/'entry.o'),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('Transmit DMA relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    entry=next(s for s in elf.sections if s['name']=='.entry')
    entry_data=elf.contents(entry)
    assert len(entry_data)==4 and not elf.relocations(entry['index'])
    rows.append({'symbol':'open_cfw_gx8002_uart_transmit_dma_entry','compiled_bytes':4,'compiled_sha256':sha(entry_data),'stock_sha256':sha(stock[0xc694:0xc71c]),'package_offset':0xc694,'envelope_bytes':136,'fits':True})
    return {'entry_source_sha256':sha(entry_source.read_bytes()),'placement_limits':['Relocated body occupies transferred udivdi3 fill; paired admission verifies ownership and entry redirect.'],'sdk_commit':SDK_COMMIT,'upstream_header':header,'upstream_blob':blob,'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. Invalid-port cleanup is an explicit repair, not stock equivalence. Decoded DMA setup behavior and upstream config layout qualification pending; called helpers remain separate dependencies.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-transmit-dma-placement-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
