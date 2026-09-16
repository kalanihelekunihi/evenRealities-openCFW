# SPDX-License-Identifier: MIT
"""Build authenticated SPL clock trimming source for stage one."""
import json,re,subprocess
from build_gx8002_stage1_clock_initialize import build as initialize,ROOT,SDK_COMMIT,authenticated_blob,sha,Elf32,IMAGE,IMAGE_SHA
from verify_gx8002_analog_source import FLAGS


def build():
    evidence=initialize();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-stage1-clock-trim';out.mkdir(exist_ok=True)
    rel='arch/soc/grus/spl/spl_clk.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream=authenticated_blob(sdk/rel,blob).decode()
    cfg='include/driver/grus_cfg.h';cfg_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+cfg],text=True).strip();cfg_data=authenticated_blob(sdk/cfg,cfg_blob)
    body=upstream[upstream.index('void spl_clk_set_source'):upstream.index('int spl_clk_set_pll_no_block')]
    body+=upstream[upstream.index('void spl_clk_set_gate_enable'):upstream.index('int spl_clk_get_frequence')]
    body+=upstream[upstream.index('static inline void _osc_set_32k_trim_value'):upstream.index('void spl_clk_init(void)')]
    body=body.replace('int i = 0;', 'unsigned int i = 0;')
    body=re.sub(r'^(?:static (?:inline )?)?(void|int) (?!spl_clk_trim\b)(\w+)\(',r'static inline __attribute__((always_inline)) \1 \2(',body,flags=re.M)
    body=body.replace('unsigned int trim_', 'uint32_t trim_')
    source_tables=re.findall(r'static GX_CLOCK_SOURCE_TABLE (?:clk_low_table|clk_src_high_table)\[\] = \{.*?\};',body,re.S)
    assert len(source_tables)==2
    for table in source_tables:body=body.replace(table,'')
    body='\n'.join(t.replace('static GX_CLOCK_SOURCE_TABLE','GX_CLOCK_SOURCE_TABLE',1) for t in source_tables)+'\n'+body
    # Do not turn the external flash API into an inline definition.
    source=out/'trim.c';source.write_text('#include <stddef.h>\n#include <stdint.h>\n#include <clk_priv.h>\n#include <base_addr.h>\n#include "grus_cfg.h"\n#define DCACHE_LINE_SIZE 16\n_Static_assert(sizeof(struct grus_cfg)==64,"flash configuration size");\n'+body)
    (out/'grus_cfg.h').write_bytes(cfg_data)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (out/'clk_priv.h').write_bytes((ROOT/'build/gx8002-stage1-clock-initialize/clk_priv.h').read_bytes())
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-delete-null-pointer-checks']
    subprocess.run([pre+'gcc',*flags,'-isystem',str(out),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(source),'-o',str(out/'trim.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(out/'trim.o'),str(out/'global.o')],check=True)
    ld='''SECTIONS {
.text 0x100004f4 : { *(.text.spl_clk_trim) }
.data.gx_clock_param_table 0x200014c8 : { *(.data.gx_clock_param_table) }
.data.low 0x20001668 : { *(.data.clk_low_table* .rodata.clk_low_table*) }
.data.high 0x20001678 : { *(.data.clk_src_high_table* .rodata.clk_src_high_table*) }
.data.gx_clock_dto_table 0x200016d8 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x200016dc : { *(.data.gx_clock_div_table) }
/DISCARD/ : { *(.text.__module_get_info) }
.analysis_helpers 0x10004000 : { *(.text*) *(.rodata*) }
}
__module_get_info = 0x10000138;
sflash_readdata = 0x10000fdc;
'''
    (out/'trim.ld').write_text(ld);path=out/'trim.elf'
    subprocess.run([pre+'ld','-T',str(out/'trim.ld'),str(out/'global.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trim');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    for section in elf.sections:
        if section['name'].startswith('.data.'):
            offset=section['address']-0x20000000+0x38954
            assert elf.contents(section)==stock[offset:offset+section['size']],section['name']
    (out/'trim.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    assert next(s['size'] for s in elf.sections if s['name']=='.text')<=740
    assert not any(s['name']=='.analysis_helpers' and s['size'] for s in elf.sections)
    sections=[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    report={'upstream_evidence':evidence,'source_blob':blob,'adaptations':['Force private helpers inline; unsigned loop indices; use uint32_t for trim locals to match upstream helper pointer types; expose source tables to preserve runtime table loads.'],'flags':flags,'fits':True,'configuration_blob':cfg_blob,'source_sha256':sha(source.read_bytes()),'sections':sections,'code_envelope_bytes':740,'source_admitted':False,'limits':['Build candidate only; flash return is ignored as upstream/stock, configuration magic/XOR gate trim writes. Decoded behavior, placement and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-stage1-clock-trim-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
