# SPDX-License-Identifier: MIT
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32


def build():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_cache_initialize.c'
    out=ROOT/'build/gx8002-cache-initialize';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'control.o'
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
    from verify_gx8002_csi_source import HEADERS
    dependencies=[]
    for header in (*HEADERS,'LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip()
        data=authenticated_blob(sdk/header,blob)
        dependencies.append({'path':header,'blob':blob,'sha256':sha(data)})
    command=[pre+'gcc','-Os',*FLAGS[1:]]
    for directory in ('arch/soc/grus/include','include/utility','include/utility/libc'):
        command.extend(['-isystem',str(sdk/directory)])
    subprocess.run([*command,'-c',str(source),'-o',str(obj)],check=True)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Cache initialize stock identity')
    rows=[]
    for kind,offset,size in (('initialize',0xd1cc,32),):
        symbol='open_cfw_gx8002_cache_'+kind;script=out/(kind+'.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } /DISCARD/ : { *(.text*) } }\ngx_icache_enable = 0x1002571c;\ngx_dcache_disable = 0x100255e4;\ngx_dcache_enable = 0x100255c4;\n'%(offset+0x101f6a74,symbol))
        target=out/(kind+'.elf');subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(target)],check=True)
        elf=Elf32(target.read_bytes(),str(target));sec=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(sec)
        if elf.relocations(sec['index']):raise ValueError('Cache initialize relocation')
        (out/(kind+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
        rows.append({'symbol':symbol,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_sha256':sha(stock[offset:offset+size]),'package_offset':offset,'envelope_bytes':size,'fits':len(data)<=size})
    return {'sdk_commit':SDK_COMMIT,'upstream_dependencies':dependencies,'functions':rows,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Build only. Cache helper ordering and CSI region write qualification pending.']}

if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-cache-initialize-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
