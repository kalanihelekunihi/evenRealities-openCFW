# SPDX-License-Identifier: MIT
"""Compile upstream frequency logic with the stage1's inline divider path."""
import json,subprocess
from build_gx8002_backup_platform_gate import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_analog_source import FLAGS
from build_gx8002_stage1_clock_tables import build as tables_build


def build():
    table_evidence=tables_build();evidence=authenticate();out=ROOT/'build/gx8002-stage1-clock-frequency';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    # The stage1 inlines divider reads. Use the authenticated upstream header
    # directly rather than the primary image's two-register divider adapter.
    header=(sdk/'arch/soc/grus/include/clk_priv.h').read_bytes()
    (out/'clk_priv_frequency.h').write_bytes(header)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_clock_frequency.c'
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-delete-null-pointer-checks']
    subprocess.run([pre+'gcc',*flags,'-isystem',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(out/'frequency.o')],check=True)
    (out/'frequency.ld').write_text('''SECTIONS {
.lookup 0x10000138 : { *(.text.__module_get_info) }
.data.gx_clock_param_table 0x200014c8 : { *(.data.gx_clock_param_table) }
.data.gx_clock_dto_table 0x200016d8 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x200016dc : { *(.data.gx_clock_div_table) }
.text 0x10000300 : { *(.text.open_cfw_gx8002_clock_frequency) }
.rodata 0x100013b8 : { *(.rodata.open_cfw_gx8002_clock_frequency) }
/DISCARD/ : { *(.text*) *(.data*) *(.rodata*) }
}
''')
    subprocess.run([pre+'ld','-T',str(out/'frequency.ld'),str(out/'frequency.o'),'-o',str(out/'frequency.elf')],check=True)
    elf=Elf32((out/'frequency.elf').read_bytes(),'stage1 frequency');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    independent=Elf32((ROOT/'build/gx8002-stage1-clock-tables/tables.elf').read_bytes(),'independent lookup')
    for section in independent.sections:
        if section['flags']&2 and section['size']:
            name='.lookup' if section['name']=='.text' else section['name']
            linked=next(s for s in elf.sections if s['name']==name)
            assert linked['address']==section['address'] and elf.contents(linked)==independent.contents(section)
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,address,size in (('.text',0x10000300,500),('.rodata',0x100013b8,76)):
        section=next(s for s in elf.sections if s['name']==name);body=elf.contents(section)
        assert section['address']==address and not elf.relocations(section['index'])
        rows.append({'section':name,'address':address,'compiled_bytes':len(body),'compiled_sha256':sha(body),
                     'envelope_bytes':size,'fits':len(body)<=size})
    (out/'frequency.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'frequency.elf')],text=True))
    report={'lookup_and_tables':table_evidence,'upstream_evidence':evidence,'header_sha256':sha(header),'source_sha256':sha(source.read_bytes()),'flags':flags,
            'sections':rows,'source_admitted':False,'hardware_qualified':False,
            'limits':['Candidate only: unchanged authenticated upstream frequency arithmetic with inline divider.',
                      'Lookup and tables linked from source at original BINH stage-one addresses; physical hardware, references and loader not qualified.']}
    (ROOT/'docs/research/gx8002-stage1-clock-frequency-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build()['sections'],indent=2))
