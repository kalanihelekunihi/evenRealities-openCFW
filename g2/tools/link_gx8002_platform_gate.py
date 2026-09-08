#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link upstream clock gate at stock entries without behavior admission."""
import json
import subprocess
from verify_gx8002_clock_tables import verify as tables
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE, sha
from link_gx8002_uart_console import ROOT


def link():
    evidence=tables();output=ROOT/'build/gx8002-platform-gate';sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    flags=['-Os',*FLAGS[1:],'--param=case-values-threshold=3','-fno-gcse','-fno-tree-forwprop']
    obj=output/'gate-fit.o'
    subprocess.run([str(prefix)+'gcc',*flags,'-I',str(output),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(ROOT/'components/shared/gx8002/runtime_gx8002_platform_gate.c'),'-o',str(obj)],check=True)
    # Expose the local source symbol so the linker can bind calls to the
    # independently qualified helper, instead of this compilation's variant.
    global_obj=output/'gate-fit-global.o'
    subprocess.run([str(prefix)+'objcopy','--globalize-symbol=__module_get_info',str(obj),str(global_obj)],check=True)
    script=output/'gate-fit.ld'
    script.write_text('''SECTIONS {
.text.open_cfw_gx8002_platform_gate 0x10025080 : { *(.text.open_cfw_gx8002_platform_gate) }
.rodata.open_cfw_gx8002_platform_gate 0x100253cc : { *(.rodata.open_cfw_gx8002_platform_gate) }
.data.gx_clock_param_table 0x200266e0 : { *(.data.gx_clock_param_table) }
.data.gx_clock_dto_table 0x20026880 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x20026884 : { *(.data.gx_clock_div_table) }
/DISCARD/ : { *(.text.__module_get_info) *(.text.open_cfw_gx8002_clock_lookup) }
}
__module_get_info = 0x10024a44;
''')
    linked=output/'gate-fit.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(global_obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes();rows=[]
    for name,offset,address,size in [('.text.open_cfw_gx8002_platform_gate',0x17094,0x10025080,256),('.rodata.open_cfw_gx8002_platform_gate',0x173e0,0x100253cc,148)]:
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section)
        if len(payload)>size or section['address']!=address or elf.relocations(section['index']):raise ValueError('gate placement failure')
        rows.append({'section':name,'package_offset':offset,'runtime_address':address,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size])})
    report={'upstream_evidence':evidence,'flags':flags,'sections':rows,'source_admitted':False,
            'limits':['Lookup resolves to separately qualified source entry.','Gate MMIO behavior and switch-target equivalence pending; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-platform-gate-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
