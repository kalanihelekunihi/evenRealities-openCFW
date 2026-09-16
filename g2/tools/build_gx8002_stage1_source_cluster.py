# SPDX-License-Identifier: MIT
"""Compose source-built stage-one dispatcher, clock, flash and UART components."""
import json,subprocess,re
from build_gx8002_stage1_initialize import build as startup_build,ROOT,Elf32,sha
from build_gx8002_stage1_clock_cluster import build as clock_build
from build_gx8002_stage1_flash_cluster import build as flash_build
from build_gx8002_stage1_reset import build as reset_build


def build():
    evidence={'startup':startup_build(),'clock':clock_build(),'flash':flash_build(),'reset':reset_build()}
    out=ROOT/'build/gx8002-stage1-source-cluster';out.mkdir(exist_ok=True)
    startup=ROOT/'build/gx8002-stage1-initialize';clock=ROOT/'build/gx8002-stage1-clock-cluster'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    init=out/'clock-init.o'
    init_dir=ROOT/'build/gx8002-stage1-clock-initialize';sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    header=(init_dir/'clk_priv.h').read_text()
    header,count=re.subn(r'static GX_CLOCK_MODULE_PARAM gx_clock_param_table\[\] = \{.*?\n\};', 'extern GX_CLOCK_MODULE_PARAM gx_clock_param_table[26];',header,flags=re.S);assert count==1
    (out/'clk_priv.h').write_text(header)
    subprocess.run([pre+'gcc',*json.loads((ROOT/'docs/research/gx8002-stage1-clock-initialize-candidate.json').read_text())['flags'],'-isystem',str(out),'-isystem',str(init_dir),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-c',str(init_dir/'initialize.c'),'-o',str(out/'clock-raw.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(out/'clock-raw.o'),str(init)],check=True)
    subprocess.run([pre+'objcopy','--weaken-symbol=__module_get_info',str(init)],check=True)
    frequency=out/'frequency-global.o'
    subprocess.run([pre+'objcopy','--globalize-symbol=gx_clock_param_table',str(startup/'frequency-global.o'),str(frequency)],check=True)
    ld=(startup/'initialize.ld').read_text()
    extra='\n'.join(line for line in (clock/'cluster.ld').read_text().splitlines() if line.startswith(('.clock_trim ','.data.low ','.data.high ','.trim_all ','.trim_32k ','.board ','.text ','.rodata ','.data.clock_source_table ')))
    extra=extra.replace('.text ','.clock_initialize ',1).replace('.rodata ','.clock_initialize_switch ',1)
    extra+='\n.read 0x10000edc : { *(.text.sflash_read_reg) }\n.write 0x10000f5c : { *(.text.sflash_write_reg) }\n.flash 0x10000fdc : { *(.text.sflash_readdata) *(.text.wait_till_ready) }\n.data.flash 0x20001730 : { *(.data.flash_jedec) }\n'
    extra+='\n.vectors 0x10000000 : { *(.spl.vectors) }\n.reset 0x10000100 : { *reset.o(.text) }\n'
    ld=re.sub(r'^\.empty_hook .*\n','',ld,flags=re.M)
    ld=ld.replace('/DISCARD/ : {','/DISCARD/ : { *(.text.open_cfw_gx8002_stage1_38a88) ',1)
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('/DISCARD/ : {','/DISCARD/ : { *clock-init.o(.text.__module_get_info .text.open_cfw_stage1_lookup_contract .data.gx_clock_*) *trim-input.o(.text.__module_get_info .data.gx_clock_*) ',1)
    ld=ld.replace('open_cfw_gx8002_stage1_3912c = 0x100007d8;','open_cfw_gx8002_stage1_3912c = spl_clk_init;')
    ld=ld.replace('open_cfw_gx8002_loader_flash_read = 0x10000fdc;','open_cfw_gx8002_loader_flash_read = sflash_readdata;')
    ld+='spl_clk_set_gate_enable = open_cfw_gx8002_platform_gate;\nopen_cfw_gx8002_stage1_clock_trim = spl_clk_trim;\nspl_osc_set_32k_trim_state = open_cfw_gx8002_stage1_3980c;\nspl_osc_set_all_trim_state = open_cfw_gx8002_stage1_397f4;\n'
    ld+='spl_board_init_r = open_cfw_gx8002_stage1_initialize;\nopen_cfw_gx8002_stage1_38a88 = spl_clear_bss;\nreset_handler = 0x10003100;\nENTRY(spl_reset_handler)\n'
    (out/'cluster.ld').write_text(ld)
    objects=[startup/name for name in ('initialize.o','hooks.o','frequency-global.o','gate-global.o')]
    objects=[frequency if x.name=='frequency-global.o' else x for x in objects]
    objects += [ROOT/'build'/name for name in ('gx8002-stage1-divmod/divmod.o','gx8002-stage1-uart-configure/uart.o','gx8002-stage1-clock-control/state.o','gx8002-stage1-peripheral-shutdown/state.o','gx8002-stage1-boot-state/state.o','gx8002-backup-loader/loader.o','gx8002-stage1-clock-cluster/trim-input.o','gx8002-stage1-clock-initialize/board.o','gx8002-stage1-trim-setters/setters.o','gx8002-stage1-flash-read/global.o','gx8002-stage1-reset/reset.o')]
    path=out/'cluster.elf';subprocess.run([pre+'ld','-T',str(out/'cluster.ld'),*map(str,objects),str(init),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'stage1 source cluster')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    absolute=[s for s in elf.symbols() if s['section']==0xfff1 and s['type']!=4 and s['name']]
    assert len(absolute)==1 and absolute[0]['name']=='reset_handler' and absolute[0]['value']==0x10003100
    mappings=[(startup/'initialize.elf',{}),(clock/'cluster.elf',{'.text':'.clock_initialize','.rodata':'.clock_initialize_switch'}),(ROOT/'build/gx8002-stage1-flash-cluster/cluster.elf',{'.text':'.flash','.data':'.data.flash'})]
    mappings.append((ROOT/'build/gx8002-stage1-reset/reset.elf',{}))
    for original_path,mapping in mappings:
        original=Elf32(original_path.read_bytes(),'component')
        for section in original.sections:
            if not section['flags']&2 or not section['size']:continue
            if section['name']=='.empty_hook':
                reset=next(s for s in elf.sections if s['name']=='.reset')
                assert elf.contents(reset)[52:54]==original.contents(section)
                continue
            linked=next(s for s in elf.sections if s['name']==mapping.get(section['name'],section['name']))
            assert linked['address']==section['address'] and elf.contents(linked)==original.contents(section),(original_path,section['name'])
    ranges=sorted((s['address']&0xfffffff,(s['address']&0xfffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'components':evidence,'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Source reset/vector code linked with source dispatcher and shared empty hook. Only absolute implementation dependency is later-image reset at 0x10003100. Complete composed execution, fallback-image lifetime, loader overlap and full firmware admission remain pending.']}
    (ROOT/'docs/research/gx8002-stage1-source-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
