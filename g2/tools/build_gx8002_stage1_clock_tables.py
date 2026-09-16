# SPDX-License-Identifier: MIT
"""Rebuild stage1 clock parameter tables and lookup from authenticated upstream."""
import json,subprocess
from build_gx8002_backup_platform_gate import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-stage1-clock-tables';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-delete-null-pointer-checks']
    subprocess.run([pre+'gcc',*flags,'-I',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(ROOT/'components/shared/gx8002/runtime_gx8002_platform_gate.c'),'-o',str(out/'lookup.o')],check=True)
    (out/'tables.ld').write_text('''SECTIONS {
.text 0x10000138 : { *(.text.__module_get_info) }
.data.gx_clock_param_table 0x200014c8 : { *(.data.gx_clock_param_table) }
.data.gx_clock_dto_table 0x200016d8 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x200016dc : { *(.data.gx_clock_div_table) }
/DISCARD/ : { *(.text*) *(.rodata*) }
}
''')
    subprocess.run([pre+'ld','-T',str(out/'tables.ld'),str(out/'lookup.o'),'-o',str(out/'tables.elf')],check=True)
    elf=Elf32((out/'tables.elf').read_bytes(),'stage1 clock tables');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size in [('param',0x200014c8,416),('dto',0x200016d8,3),('div',0x200016dc,68)]:
        section=next(s for s in elf.sections if s['name']=='.data.gx_clock_'+name+'_table')
        data=elf.contents(section);offset=address-0x20000000+0x38954
        assert section['address']==address and len(data)==size and not elf.relocations(section['index'])
        assert data==stock[offset:offset+size],name
        rows.append({'section':section['name'],'runtime_address':address,'package_offset':offset,'bytes':size,'sha256':sha(data),'byte_exact':True})
    section=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(section)
    assert section['address']==0x10000138 and len(body)<=192 and not elf.relocations(section['index'])
    (out/'lookup.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'tables.elf')],text=True))
    result={'upstream_evidence':evidence,'flags':flags,'tables':rows,'source_table_bytes':sum(r['bytes'] for r in rows),
            'lookup':{'compiled_bytes':len(body),'compiled_sha256':sha(body),'envelope_bytes':192,'runtime_address':0x10000138,'package_offset':0x38a8c},
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Source-defined parameter/DTO/divider tables match stage1 bytes after pointer relocation.',
                      'Lookup behavior, external references and loader qualification pending; padding excluded.']}
    (ROOT/'docs/research/gx8002-stage1-clock-tables-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    r=build();print(r['source_table_bytes'],'table bytes;',r['lookup']['compiled_bytes'],'lookup bytes')
