#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed Clock initialization call/state sequence; no source admission."""
import json,subprocess,re
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'gx_clock_set_div':0x10024df8,'gx_clock_set_dto':0x10024f44,'gx_clock_set_module_source':0x10024be0,'gx_clock_set_source':0x10024bcc,'gx_clock_set_module_enable':0x10025080,'gx_pmu_get_start_mode':0x10024984,'gx_pmu_osc_get_all_trim_state':0x10024a1c,'gx_clock_set_pll_no_block':0x1002500c,'gx_clock_set_pll':0x10025060,'gx_analog_set_ldo_ana_voltage':0x100246f0,'gx_analog_set_ldo_dig_voltage':0x10024730,'pll':0x200268c8,'s_clk_mod_gate':0x20027318,'memcpy':0x10025738}
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';rel='boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();oracle=authenticated_blob(sdk/rel,blob)
    header_rel='include/driver/gx_clock.h';header_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header_rel],text=True).strip();header=authenticated_blob(sdk/header_rel,header_blob)
    dependency_headers={}
    for dependency in ('arch/soc/grus/include/base_addr.h','include/driver/gx_clock/gx_clock_v2.h'):
        dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+dependency],text=True).strip()
        dep_data=authenticated_blob(sdk/dependency,dep_blob)
        dependency_headers[dependency]={'blob':dep_blob,'sha256':sha(dep_data)}
    config=out/'clock-init-pointer-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config/'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    declarations=''
    for rel_header in ('include/driver/gx_pmu_ctrl.h','include/driver/gx_pmu_osc.h','include/driver/gx_analog/gx_ldo.h'):
        hblob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel_header],text=True).strip();hdata=authenticated_blob(sdk/rel_header,hblob);dependency_headers[rel_header]={'blob':hblob,'sha256':sha(hdata)};ht=hdata.decode()
        for enum in re.findall(r'typedef enum\s*\{[^}]+\}\s*\w+;',ht):
            if any(n in enum for n in ('GX_START_MODE;', 'GX_ANALOG_LDO_ANA_VOLTAGE;', 'GX_ANALOG_LDO_DIG_VOLTAGE;')):declarations+=enum+'\n'
        for name in ('gx_pmu_get_start_mode','gx_pmu_osc_get_all_trim_state','gx_analog_set_ldo_ana_voltage','gx_analog_set_ldo_dig_voltage'):
            m=re.search(r'^\w+ '+name+r'\([^;]+;',ht,re.M)
            if m:declarations+=m[0]+'\n'
    text=oracle.decode()
    tables=text[text.index('static GX_CLOCK_SOURCE_TABLE clk_src_xtal_table'):text.index('/*********************** PLL CONFIG')]
    startup=text[text.index('static int _clk_pll_init'):text.index('static void _clk_mod_lowpower_init')]
    startup=startup.replace('int i;', 'unsigned int i;').replace('for (int i = 0;', 'for (unsigned int i = 0;')
    startup=startup.replace('CLOCK_MODULE_AUDIO_IN_PDM, MODULE_SOURCE_PDM_SYS', 'CLOCK_MODULE_AUDIO_IN_PDM, MODULE_SOURCE_PDM_OSC_1M')
    dividers=text[text.index('static void _clk_pmu_normal_div_dto'):text.index('static void _clk_pmu_lowpower_div_dto')]+text[text.index('static void _clk_mcu_normal_div_dto'):text.index('static void _clk_mcu_lowpower_div_dto')]
    main=text[text.index('void clk_init(void)'):text.index('void board_init(void)')].replace('void clk_init(void)', 'void open_cfw_gx8002_clock_init_pointer(void)').replace('for (int i = 0;', 'for (unsigned int i = 0;')
    begin=startup.index('static void _clk_src_init(void)')
    end=startup.index('static void _clk_mod_normal_init(void)')
    startup=startup[:begin]+"""static void _clk_src_init(void)
{
    GX_CLOCK_SOURCE_TABLE *table = clk_src_xtal_table;
    if (gx_pmu_osc_get_all_trim_state() == 1) {
        stage2_trim_done = 1;
        if (_clk_pll_init() == -1) while (1);
        table = clk_src_osc_table;
    }
    for (GX_CLOCK_SOURCE_TABLE *p = table; p != table + 10; ++p)
        gx_clock_set_source(p);
}

"""+startup[end:]
    body='extern GX_CLOCK_PLL pll;\nextern unsigned int s_clk_mod_gate;\n'+tables+startup+dividers+main
    source=out/'clock-init-pointer.c';source.write_text('#include <driver/gx_clock.h>\n#include <base_addr.h>\n#define SRAM_DIV_PARAM 1\n#define MCU_DIV_PARAM 3\n#define NPU_DIV_PARAM 1\n#define FLASH_DIV_PARAM 1\n'+declarations+body);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:],'-fno-jump-tables']
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(source),'-o',str(out/'clock-init-pointer-candidate.o')],check=True)
    script=out/'clock-init-pointer-candidate.ld';script.write_text('SECTIONS { .text 0x10025a88 : { *(.text.open_cfw_gx8002_clock_init_pointer) } .trim 0x20026900 : { *(.data.stage2_trim_done) } .osc 0x20026904 : { *(.data.clk_src_osc_table) } .xtal 0x20026954 : { *(.data.clk_src_xtal_table) } .rodata 0x10025ce0 : { *(.rodata*) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    p=out/'clock-init-pointer-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'clock-init-pointer-candidate.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));sec=next(s for s in e.sections if s['name']=='.text');payload=e.contents(sec);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or e.relocations(sec['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('Clock initialization stock/link')
    (out/'clock-init-pointer-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'recovered_configuration':{'SRAM_DIV_PARAM':1,'MCU_DIV_PARAM':3,'NPU_DIV_PARAM':1,'FLASH_DIV_PARAM':1,'PLL_frequency':'default 24.576 MHz','dynamic_CPU_frequency':False,'AIN_AOUT_same_clock':False},'dependency_headers':dependency_headers,'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(oracle),'role':'compiled_upstream_with_explicit_PDM_and_loop_index_adaptations'},'bindings':BINDINGS,'flags':flags,'header':{'path':header_rel,'blob':header_blob,'sha256':sha(header)},'source_sha256':sha(source.read_bytes()),'symbol':'open_cfw_gx8002_clock_init_pointer','section_name':'.text','package_offset':0x17a9c,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':564,'stock_sha256':sha(stock[0x17a9c:0x17cd0]),'fits':len(payload)<=564,'source_admitted':False,'limits':['Unadmitted full initialization candidate; data placement and decoded validation pending. Crystal/oscillator selector paths share one pointer loop with the same ten-entry bounds. PDM source adapted to stock OSC_1M policy; unsigned fixed-size loop indices avoid signedness warnings. Build evidence only; see the separate decoded qualification and composed execution reports. Full driver state ownership and hardware qualification remain incomplete.']}
    report['data_sections']=[]
    for name,offset,size in (('.trim',0x18914,4),('.osc',0x18918,80),('.xtal',0x18968,80),('.rodata',0x17cf4,36)):
        section=next(s for s in e.sections if s['name']==name);data=e.contents(section)
        assert len(data)==size and data==stock[offset:offset+size],(name,data.hex(),stock[offset:offset+size].hex())
        report['data_sections'].append({'name':name,'package_offset':offset,'bytes':size,'sha256':sha(data),'stock_exact':True})
    (ROOT/'docs/research/gx8002-clock-init-pointer-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
