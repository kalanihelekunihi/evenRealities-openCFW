# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_fifo_depth.c'
    out=ROOT/'build/gx8002-uart-fifo-depth';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'control.o'
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
    header='include/driver/gx_uart.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,blob)
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Receive DMA stock identity')
    rows=[]
    for kind,offset,size in (('fifo_depth',0xc8ec,104),):
        symbol='open_cfw_gx8002_uart_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('Receive DMA relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    return {'sdk_commit':SDK_COMMIT,'upstream_header':header,'upstream_blob':blob,'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. Decoded FIFO parameter mapping requires separate verification.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-fifo-depth-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
