#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed Module gate query call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'__module_get_info':0x10024a44,'gx_clock_param_table':0x200266e0}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='arch/soc/grus/include/clk_priv.h';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_clock.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'clock-gate-query-fixed-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    text=oracle.decode()
    prelude=text[text.index('#include'):text.index('static GX_CLOCK_DIV gx_clock_div_table')]
    body=text[text.index('static inline int _clk_get_all_gate'):text.index('static inline void _clk_set_high_gate')]
    body=body.replace('static inline int _clk_get_all_gate','int open_cfw_gx8002_clock_gate_query_fixed')
    body=body.replace('int i = module;', 'GX_CLOCK_MODULE_PARAM *child = info.param;').replace('gx_clock_param_table[++i].gate_all_offs', '(++child)->gate_all_offs')
    source=out/'clock-gate-query-fixed.c'
    source.write_text('#include <stdint.h>\n#include <stddef.h>\n'+prelude+'extern int __module_get_info(GX_CLOCK_MODULE,GX_CLOCK_MODULE_INFO *);\nextern GX_CLOCK_MODULE_PARAM gx_clock_param_table[];\n'+body)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-jump-tables','-fno-tree-ter']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'clock-gate-query-fixed-candidate.o')],check=True)
    script=out/'clock-gate-query-fixed-candidate.ld';script.write_text('SECTIONS { .text 0x10025180 : { *(.text.open_cfw_gx8002_clock_gate_query_fixed) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'clock-gate-query-fixed-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'clock-gate-query-fixed-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('Module gate query stock/link')
    (out/'clock-gate-query-fixed-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'adaptations':['Resolve grouped child gate offsets relative to the looked-up parent row instead of indexing the permuted table by module ID.'],'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'upstream_with_resolved_parent_child_index_fix'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_clock_gate_query_fixed','section_name':'.text','package_offset':0x17194,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':108,'stock_sha256':sha(stock[0x17194:0x17200]),'fits':len(payload)<=108,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    (ROOT/'docs/research/gx8002-clock-gate-query-fixed-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
