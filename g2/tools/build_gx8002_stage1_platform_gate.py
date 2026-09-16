# SPDX-License-Identifier: MIT
"""Build authenticated upstream GRUS clock gate at stage1 addresses."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    out=ROOT/'build/gx8002-stage1-platform-gate';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_platform_gate.c';dependencies=[]
    for name in ('arch/soc/grus/include/clk_priv.h','arch/soc/grus/include/base_addr.h','include/driver/gx_clock.h','include/driver/gx_clock/gx_clock_v2.h','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        dependencies.append({'path':name,'blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    flags=['-Os',*FLAGS[1:],'--param=case-values-threshold=3','-fno-gcse','-fno-tree-forwprop']
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(out/'gate.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(out/'gate.o'),str(out/'global.o')],check=True)
    (out/'gate.ld').write_text('''SECTIONS {
.text 0x100001f8 : { *(.text.open_cfw_gx8002_platform_gate) }
.rodata 0x10001324 : { *(.rodata.open_cfw_gx8002_platform_gate) }
/DISCARD/ : { *(.text*) *(.data*) *(.rodata*) }
}
__module_get_info = 0x10000138;
''')
    subprocess.run([pre+'ld','-T',str(out/'gate.ld'),str(out/'global.o'),'-o',str(out/'gate.elf')],check=True)
    elf=Elf32((out/'gate.elf').read_bytes(),'stage1 gate');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size in (('.text',0x100001f8,264),('.rodata',0x10001324,148)):
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section)
        assert section['address']==address and not elf.relocations(section['index'])
        offset=address-0x10000000+0x38954
        rows.append({'section':name,'runtime_address':address,'package_offset':offset,'compiled_bytes':len(payload),
                     'compiled_sha256':sha(payload),'envelope_bytes':size,'fits':len(payload)<=size,
                     'stock_sha256':sha(stock[offset:offset+size])})
    (out/'gate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'gate.elf')],text=True))
    result={'sdk_commit':SDK_COMMIT,'dependencies':dependencies,'flags':flags,'source_sha256':sha(source.read_bytes()),
            'lookup_runtime_address':0x10000138,'sections':rows,'source_admitted':False,'hardware_qualified':False,
            'limits':['Upstream gate and source-generated jump tables only; lookup remains bound to retained stage1 entry.',
                      'Branch-table mapping, lookup/table semantics, MMIO equivalence and loader qualification pending.']}
    (ROOT/'docs/research/gx8002-stage1-platform-gate-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(build(),indent=2))
