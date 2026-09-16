# SPDX-License-Identifier: MIT
"""Build pinned SPL clock initialization source; analysis candidate only."""
import json,subprocess,re
from build_gx8002_stage1_platform_gate import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_stage1_trim_setters import verify as trim_setters


def build():
    trim_evidence=trim_setters();evidence=authenticate();sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    rel='arch/soc/grus/spl/spl_clk.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    upstream=authenticated_blob(sdk/rel,blob).decode()
    body=upstream[upstream.index('static GX_CLOCK_SOURCE_TABLE clock_source_table'):upstream.index('int spl_clk_set_pll_no_block')]
    body+=upstream[upstream.index('void spl_clk_set_gate_enable'):upstream.index('static inline void _osc_set_32k_trim_value')]
    body+=upstream[upstream.index('void spl_clk_init(void)'):]
    body=body.replace('int i;', 'unsigned int i;').replace('int i = 0;', 'unsigned int i = 0;')
    out=ROOT/'build/gx8002-stage1-clock-initialize';out.mkdir(exist_ok=True)
    header=(sdk/'arch/soc/grus/include/clk_priv.h').read_text()
    header=header.replace('static inline ', 'static inline __attribute__((always_inline)) ')
    header=header.replace('static void __reg_set_val', 'static inline __attribute__((always_inline)) void __reg_set_val')
    (out/'clk_priv.h').write_text(header)
    body=re.sub(r'^(?:static )?(void|int) (?!spl_clk_init\b)(\w+)\(',r'static inline __attribute__((always_inline)) \1 \2(',body,flags=re.M)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=out/'initialize.c';source.write_text('#include <stddef.h>\n#include <stdint.h>\n#include <clk_priv.h>\n#include <base_addr.h>\nextern void spl_osc_set_32k_trim_state(int);\nextern void spl_osc_set_all_trim_state(int);\nextern void spl_board_clk_init(void);\n'+body+'\nint open_cfw_stage1_lookup_contract(GX_CLOCK_MODULE m, GX_CLOCK_MODULE_INFO *p) { return __module_get_info(m,p); }\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:],'-fno-delete-null-pointer-checks','-fno-tree-loop-optimize']
    subprocess.run([pre+'gcc',*flags,'-isystem',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(out/'initialize.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(out/'initialize.o'),str(out/'global.o')],check=True)
    board_source=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_board_clock.c'
    subprocess.run([pre+'gcc',*flags,'-c',str(board_source),'-o',str(out/'board.o')],check=True)
    bindings={'__module_get_info':0x38a8c,'open_cfw_gx8002_stage1_clock_trim':0x38e48}
    ld='SECTIONS {\n.trim_all 0x10000ea0 : { *(.text.open_cfw_gx8002_stage1_397f4) }\n.trim_32k 0x10000eb8 : { *(.text.open_cfw_gx8002_stage1_3980c) }\n.board 0x10001310 : { *(.text.spl_board_clk_init) }\n.text 0x100007d8 : { *(.text.spl_clk_init) }\n.rodata 0x10001404 : { *(.rodata.spl_clk_init) }\n.data.gx_clock_param_table 0x200014c8 : { *(.data.gx_clock_param_table) }\n.data.clock_source_table 0x20001688 : { *(.data.clock_source_table .rodata.clock_source_table) }\n.data.gx_clock_dto_table 0x200016d8 : { *(.data.gx_clock_dto_table) }\n.data.gx_clock_div_table 0x200016dc : { *(.data.gx_clock_div_table) }\n/DISCARD/ : { *(.text.__module_get_info .text.open_cfw_stage1_lookup_contract) }\n.analysis_helpers 0x10004000 : { *(.text*) *(.rodata*) }\n}\n'
    ld+=''.join(f'{name} = {off-0x38954+0x10000000:#x};\n' for name,off in bindings.items())
    ld+='spl_osc_set_32k_trim_state = open_cfw_gx8002_stage1_3980c;\nspl_osc_set_all_trim_state = open_cfw_gx8002_stage1_397f4;\n'
    (out/'initialize.ld').write_text(ld)
    subprocess.run([pre+'ld','-T',str(out/'initialize.ld'),str(out/'global.o'),str(out/'board.o'),str(ROOT/'build/gx8002-stage1-trim-setters/setters.o'),'-o',str(out/'initialize.elf')],check=True)
    elf=Elf32((out/'initialize.elf').read_bytes(),'SPL initialize');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'initialize.elf')],text=True))
    sections=[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name']=='.analysis_helpers' and s['size'] for s in elf.sections)
    assert next(s['size'] for s in elf.sections if s['name']=='.text')<=0x39678-0x3912c
    assert next(s['size'] for s in elf.sections if s['name']=='.rodata')<=0x14c8-0x1404
    for section in elf.sections:
        if section['name'].startswith('.data.'):
            offset=section['address']-0x20000000+0x38954
            assert elf.contents(section)==stock[offset:offset+section['size']],section['name']
    trim_elf=Elf32((ROOT/'build/gx8002-stage1-trim-setters/setters.elf').read_bytes(),'trim')
    for name,original in (('.trim_all','.setter0'),('.trim_32k','.setter1')):
        assert elf.contents(next(s for s in elf.sections if s['name']==name))==trim_elf.contents(next(s for s in trim_elf.sections if s['name']==original))
    board=next(s for s in elf.sections if s['name']=='.board');assert board['size']<=20
    physical=sorted((s['address']&0xfffffff,(s['address']&0xfffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(physical,physical[1:]))
    report={'trim_setters':trim_evidence,'board_source_sha256':sha(board_source.read_bytes()),'upstream_evidence':evidence,'upstream_path':rel,'upstream_blob':blob,'source_sha256':sha(source.read_bytes()),'adapted_header_sha256':sha(header.encode()),'flags':flags,'adaptations':['Force private upstream helpers inline, preserve lookup boundary; unsigned fixed-count loop indices.'],'code_envelope_bytes':1356,'fits':True,'sections':sections,'bindings':bindings,'source_admitted':False,'limits':['All compiled code and tables fit original envelopes; decoded behavioral comparison, reference qualification and integration pending. Trim setters and board hook linked as source. Clock-trim and lookup implementations remain absolute dependencies; board hook behavioral qualification pending.']}
    (ROOT/'docs/research/gx8002-stage1-clock-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':print(build()['sections'])
