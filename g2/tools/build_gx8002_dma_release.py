# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build(prefix=None,sdk=None,output=None):
    source=ROOT/'components/shared/gx8002/runtime_gx8002_dma_release.c'
    out=output or ROOT/'build/gx8002-dma-release';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-' if prefix is None else prefix/'csky-unknown-elf-');obj=out/'control.o'
    sdk=sdk or ROOT/'build/upstream-nationalchip-lvp-kws'
    from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
    header='include/driver/gx_dma_ahb.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
    authenticated_blob(sdk/header,blob)
    subprocess.run([pre+'gcc','-I'+str(sdk/'include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Receive DMA stock identity')
    rows=[]
    for kind,offset,size in (('release',0xd0c4,8),):
        symbol='open_cfw_gx8002_dma_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_dma_cache = 0x10025608;\nopen_cfw_gx8002_dma_deallocate = 0x10203a98;\nopen_cfw_gx8002_dma_state = 0x2002e93c;\nopen_cfw_gx8002_dma_resource = 0x10025080;\nopen_cfw_gx8002_dma_transfer = 0x10203b78;\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('Receive DMA relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    return {'sdk_commit':SDK_COMMIT,'upstream_header':header,'upstream_blob':blob,'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. Release wrapper call and ABI qualification pending; deallocation remains separate.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-dma-release-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
