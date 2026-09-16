# SPDX-License-Identifier: MIT
"""Link reconstructed stage-one dispatcher with complete source loader."""
import json,subprocess
from build_gx8002_backup_loader import build as loader
from build_gx8002_stage1_boot_state import build as boot_state
from build_gx8002_stage1_peripheral_shutdown import build as shutdown
from build_gx8002_stage1_clock_control import build as clock_control
from build_gx8002_stage1_uart_configure import build as uart_configure
from build_gx8002_stage1_divmod import build as divmod_build
from build_gx8002_stage1_clock_frequency import build as frequency_build
from build_gx8002_stage1_platform_gate import build as gate_build
from build_gx8002_backup_cfft import ROOT,FLAGS,sha,Elf32,IMAGE,IMAGE_SHA


def build():
    gate_evidence=gate_build();frequency_evidence=frequency_build();divmod_evidence=divmod_build();evidence=loader();state_evidence=boot_state();shutdown_evidence=shutdown();clock_evidence=clock_control();uart_evidence=uart_configure();out=ROOT/'build/gx8002-stage1-initialize';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_initialize.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'initialize.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
    hooks=ROOT/'components/shared/gx8002/runtime_gx8002_stage1_hooks.c';hooks_obj=out/'hooks.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(hooks),'-o',str(hooks_obj)],check=True)
    frequency_obj=out/'frequency-global.o'
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info',str(ROOT/'build/gx8002-stage1-clock-frequency/frequency.o'),str(frequency_obj)],check=True)
    gate_obj=out/'gate-global.o'
    subprocess.run([pre+'objcopy','--weaken-symbol=__module_get_info',str(ROOT/'build/gx8002-stage1-platform-gate/global.o'),str(gate_obj)],check=True)
    base=evidence['mapping_vector_package_offset'];mapping=lambda off:off-base+0x10000000
    ld=out/'initialize.ld';ld.write_text('SECTIONS {\n.gate 0x100001f8 : { *(.text.open_cfw_gx8002_platform_gate) }\n.gate_switch 0x10001324 : { *(.rodata.open_cfw_gx8002_platform_gate) }\n.lookup 0x10000138 : { *frequency-global.o(.text.__module_get_info) }\n.frequency 0x10000300 : { *(.text.open_cfw_gx8002_clock_frequency) }\n.frequency_switch 0x100013b8 : { *(.rodata.open_cfw_gx8002_clock_frequency) }\n.data.gx_clock_param_table 0x200014c8 : { *frequency-global.o(.data.gx_clock_param_table) }\n.data.gx_clock_dto_table 0x200016d8 : { *frequency-global.o(.data.gx_clock_dto_table) }\n.data.gx_clock_div_table 0x200016dc : { *frequency-global.o(.data.gx_clock_div_table) }\n'+f'.divide {mapping(0x39774):#x} : {{ *(.text.open_cfw_gx8002_stage1_39774) }}\n.remainder {mapping(0x397b8):#x} : {{ *(.text.open_cfw_gx8002_stage1_397b8) }}\n.uart {mapping(0x39bb4):#x} : {{ *(.text.open_cfw_gx8002_stage1_39bb4) }}\n.empty_hook {mapping(0x38a88):#x} : {{ *(.text.open_cfw_gx8002_stage1_38a88) }}\n.fixed_hook {mapping(0x39c34):#x} : {{ *(.text.open_cfw_gx8002_stage1_39c34) }}\n.clock_control {mapping(0x39c44):#x} : {{ *(.text.open_cfw_gx8002_stage1_39c44) }}\n.trim_predicate {mapping(0x39824):#x} : {{ *(.text.open_cfw_gx8002_stage1_39824) }}\n.shutdown {mapping(0x39b88):#x} : {{ *(.text.open_cfw_gx8002_stage1_39b88) }}\n.boot_state {mapping(0x39678):#x} : {{ *(.text.open_cfw_gx8002_stage1_39678) }}\n.loader {mapping(0x396a0):#x} : {{ *(.text.open_cfw_gx8002_backup_loader) }}\n.initialize {mapping(0x39744):#x} : {{ *(.text.open_cfw_gx8002_stage1_initialize) }}\n'+'/DISCARD/ : { *(.text.open_cfw_gx8002_uart_stage1_clear_bss) *(.text.open_cfw_gx8002_frequency_lookup) *global.o(.text.__module_get_info .text.open_cfw_gx8002_clock_lookup .data*) }\n}\n'+''.join(f'open_cfw_gx8002_stage1_{off:x} = {mapping(off):#x};\n' for off in (0x3912c,))+f'open_cfw_gx8002_stage1_frequency = open_cfw_gx8002_clock_frequency;\nopen_cfw_gx8002_stage1_gate = open_cfw_gx8002_platform_gate;\nopen_cfw_gx8002_loader_flash_read = {evidence["helper_address"]:#x};\n')
    path=out/'initialize.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),str(hooks_obj),str(frequency_obj),str(gate_obj),str(ROOT/'build/gx8002-stage1-divmod/divmod.o'),str(ROOT/'build/gx8002-stage1-uart-configure/uart.o'),str(ROOT/'build/gx8002-stage1-clock-control/state.o'),str(ROOT/'build/gx8002-stage1-peripheral-shutdown/state.o'),str(ROOT/'build/gx8002-stage1-boot-state/state.o'),str(ROOT/'build/gx8002-backup-loader/loader.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'stage1');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    sections=[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']]
    assert next(s['bytes'] for s in sections if s['name']=='.initialize')<=48
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    state_elf=Elf32((ROOT/'build/gx8002-stage1-boot-state/state.elf').read_bytes(),'standalone state')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.boot_state'))==state_elf.contents(next(s for s in state_elf.sections if s['name']=='.text'))
    shutdown_elf=Elf32((ROOT/'build/gx8002-stage1-peripheral-shutdown/state.elf').read_bytes(),'standalone shutdown')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.shutdown'))==shutdown_elf.contents(next(s for s in shutdown_elf.sections if s['name']=='.text'))
    clock_elf=Elf32((ROOT/'build/gx8002-stage1-clock-control/state.elf').read_bytes(),'standalone clock')
    for dest,original in (('.clock_control','.text'),('.trim_predicate','.predicate')):
        assert elf.contents(next(s for s in elf.sections if s['name']==dest))==clock_elf.contents(next(s for s in clock_elf.sections if s['name']==original))
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    for name,off,size in (('.empty_hook',0x38a88,2),('.fixed_hook',0x39c34,16)):
        section=next(s for s in elf.sections if s['name']==name)
        assert section['size']<=size
        if name=='.empty_hook':assert elf.contents(section)==stock[off:off+size]
    uart_elf=Elf32((ROOT/'build/gx8002-stage1-uart-configure/uart.elf').read_bytes(),'standalone UART')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.uart'))==uart_elf.contents(next(s for s in uart_elf.sections if s['name']=='.text'))
    arithmetic=Elf32((ROOT/'build/gx8002-stage1-divmod/divmod.elf').read_bytes(),'arithmetic')
    for name in ('.divide','.remainder'):
        assert elf.contents(next(s for s in elf.sections if s['name']==name))==arithmetic.contents(next(s for s in arithmetic.sections if s['name']==name))
    gate=Elf32((ROOT/'build/gx8002-stage1-platform-gate/gate.elf').read_bytes(),'gate')
    for original,name in (('.text','.gate'),('.rodata','.gate_switch')):
        section=next(s for s in gate.sections if s['name']==original)
        linked=next(s for s in elf.sections if s['name']==name)
        assert linked['address']==section['address'] and elf.contents(linked)==gate.contents(section)
    frequency=Elf32((ROOT/'build/gx8002-stage1-clock-frequency/frequency.elf').read_bytes(),'frequency')
    for section in frequency.sections:
        if section['flags']&2 and section['size']:
            name={'.text':'.frequency','.rodata':'.frequency_switch'}.get(section['name'],section['name'])
            linked=next(s for s in elf.sections if s['name']==name)
            assert linked['address']==section['address'] and elf.contents(linked)==frequency.contents(section)
    # Instruction/data SRAM aliases must not overlap in the loaded image either.
    physical=sorted((s['address']&0x0fffffff,(s['address']&0x0fffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(physical,physical[1:]))
    allocated=sorted((s['address'],s['address']+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(allocated,allocated[1:]))
    return {'gate':gate_evidence,'frequency':frequency_evidence,'arithmetic':divmod_evidence,'uart':uart_evidence,'hooks_source_sha256':sha(hooks.read_bytes()),'clock_control':clock_evidence,'shutdown':shutdown_evidence,'boot_state':state_evidence,'source_sha256':sha(src.read_bytes()),'elf_sha256':sha(path.read_bytes()),'loader':evidence,'sections':sections,'source_admitted':False,'limits':['Complete dispatcher and loader source linked at original entries. Dispatcher helper 0x3912c and flash helper remain absolute dependencies. Ordered behavioral verification and integration pending.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-stage1-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sections'])
