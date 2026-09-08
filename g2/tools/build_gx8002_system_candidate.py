#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build source startup sequence with pinned CSI helpers; not yet admitted."""
import json
import subprocess
from analyze_gx8002_upstream_objects import SDK_COMMIT, IMAGE, IMAGE_SHA, authenticated_blob, sha
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_csi_source import HEADERS
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    out=ROOT/'build/gx8002-system';out.mkdir(exist_ok=True)
    deps=[]
    for name in (*HEADERS,'arch/soc/grus/system.c','include/driver/gx_pmu_ctrl.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        deps.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_system_initialize.c'
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    flags=[*FLAGS,'-fno-expensive-optimizations']
    cmd=[str(prefix)+'gcc',*flags]
    for path in ('arch/soc/grus/include','include/utility','include/utility/libc'):cmd+=['-isystem',str(sdk/path)]
    subprocess.run([*cmd,'-c',str(source),'-o',str(out/'system.o')],check=True)
    bindings={'open_cfw_gx8002_clock_initialize':0x10025a88,
              'open_cfw_gx8002_start_mode':0x10024984,
              'open_cfw_gx8002_clear_bss':0x10023528,
              'open_cfw_gx8002_board_initialize':0x10025cbc,
              'open_cfw_gx8002_vectors':0x10023400}
    script=out/'system.ld'
    script.write_text('SECTIONS { .text 0x1002354c : { *(.text.open_cfw_gx8002_system_initialize) } }\n'+''.join(f'{name} = {address:#x};\n' for name,address in bindings.items()))
    linked=out/'system.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'system.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));section=next(s for s in elf.sections if s['name']=='.text')
    if elf.relocations(section['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved system candidate')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    dis=subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True)
    (out/'system.disassembly.txt').write_text(dis)
    report={'flags':flags,'sdk_commit':SDK_COMMIT,'dependencies':deps,'source_sha256':sha(source.read_bytes()),
            'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
            'stock_package_offset':0x15560,'stock_envelope_bytes':164,'stock_sha256':sha(stock[0x15560:0x15604]),
            'fits':section['size']<=164,'byte_exact':elf.contents(section)==stock[0x15560:0x15604],
            'bindings':bindings,'source_admitted':False,
            'limits':['Control register/MMIO/call traces require qualification.',
                      'Clock, start-mode, board and vector targets remain retained dependencies.']}
    (ROOT/'docs/research/gx8002-system-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='dependencies'},indent=2))
    return report

if __name__=='__main__':build()
