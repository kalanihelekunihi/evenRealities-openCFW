#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed Clock switch to 1 MHz call/state sequence; no source admission."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'gx_clock_set_source':0x10024bcc,'_clk_mod_lowpower_init':0x1002599c,'gx_clock_get_module_enable':0x10025180,'_clk_pmu_lowpower_div_dto':0x10025a00,'gx_clock_set_div':0x10024df8,'gx_clock_set_pll':0x10025060,'memcpy':0x10025738}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_clock.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'clock-switch-1m-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    text=oracle.decode()
    gate=text[text.index('static void _clk_mod_lowpower_gate'):text.index('/**********************************************************/',text.index('static void _clk_mod_lowpower_gate'))]
    mcu=text[text.index('static void _clk_mcu_lowpower_div_dto'):text.index('static unsigned int s_clk_mod_gate')]
    pll=text[text.index('#if (defined CONFIG_ENABLE_PLL_FREQUENCY_50M)'):text.index('static int _clk_pll_init')]
    pll=pll.replace('static GX_CLOCK_PLL pll', 'GX_CLOCK_PLL pll')
    state='unsigned int s_clk_mod_gate __attribute__((section(".bss.clock_saved_gate")));\n'
    body=text[text.index('void clk_switch_1m'):text.index('void clk_switch_soft_off')]
    body=body.replace('void clk_switch_1m','void open_cfw_gx8002_clock_switch_1m')
    body=body.replace('for (int i = 0;', 'for (unsigned int i = 0;')
    source=out/'clock-switch-1m.c'
    source.write_text('#include <driver/gx_clock.h>\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\nextern GX_CLOCK_PLL pll;\nextern unsigned int s_clk_mod_gate;\nextern void _clk_mod_lowpower_init(void);\nextern void _clk_pmu_lowpower_div_dto(void);\n'+pll+state+mcu+gate+body)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-jump-tables']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'clock-switch-1m-candidate.o')],check=True)
    script=out/'clock-switch-1m-candidate.ld';script.write_text('SECTIONS { .text 0x10025a14 : { *(.text.open_cfw_gx8002_clock_switch_1m) } .rodata 0x10025cd0 : { *(.rodata*) } .pll 0x200268c8 : { *(.data.pll) } .saved_gate 0x20027318 (NOLOAD) : { *(.bss.clock_saved_gate) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'clock-switch-1m-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'clock-switch-1m-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('Clock switch to 1 MHz stock/link')
    data_sec=next(s for s in e.sections if s['name']=='.rodata');data=e.contents(data_sec)
    assert data==stock[0x17ce4:0x17cf4] and len(data)==16
    (out/'clock-switch-1m-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'adaptations':['Unsigned loop index for two-element array avoids signedness warning without changing iteration. Helpers and PLL initializer retain upstream bodies; saved gate is source-defined zero-initialized BSS.'],'source_data':{'section_name':'.rodata','package_offset':0x17ce4,'bytes':16,'sha256':sha(data),'stock_exact':True},'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'compiled_upstream_implementation'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_clock_switch_1m','section_name':'.text','package_offset':0x17a28,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':116,'stock_sha256':sha(stock[0x17a28:0x17a9c]),'fits':len(payload)<=116,'source_admitted':False,'limits':['Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    pll_section=next(s for s in e.sections if s['name']=='.pll');pll_data=e.contents(pll_section)
    assert pll_section['address']==0x200268c8 and pll_data==stock[0x188dc:0x18914] and len(pll_data)==56
    state_section=next(s for s in e.sections if s['name']=='.saved_gate')
    assert state_section['type']==8 and state_section['address']==0x20027318 and state_section['size']==4 and state_section['flags']==3
    clear=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());interval=clear['evidence']['build']
    assert interval['bss_start']<=state_section['address']<state_section['address']+4<=interval['bss_end']
    clear_path=ROOT/'build/gx8002-clear-bss/clear.elf';clear_elf=Elf32(clear_path.read_bytes(),'startup clear');clear_row=clear['functions'][0]
    clear_section=next(s for s in clear_elf.sections if s['name']==clear_row['section_name'])
    assert sha(clear_elf.contents(clear_section))==clear_row['compiled_sha256']
    report['pll_state']={'section':'.pll','address':0x200268c8,'package_offset':0x188dc,'bytes':56,'sha256':sha(pll_data),'stock_exact':True,'configuration':'upstream default 24.576 MHz'}
    report['runtime_state']={'section':'.saved_gate','address':0x20027318,'bytes':4,'type':'NOBITS','startup_clear_elf_sha256':sha(clear_path.read_bytes()),'clear_interval':[interval['bss_start'],interval['bss_end']]}
    (ROOT/'docs/research/gx8002-clock-switch-1m-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
