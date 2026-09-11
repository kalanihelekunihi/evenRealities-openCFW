# SPDX-License-Identifier: MIT
"""Link the recovered UART configuration cluster with native-built libgcc."""
import json,subprocess
from pathlib import Path
from build_gx8002_uart_configure_object import build as build_configure,ROOT
from build_gx8002_uart_fifo_depth import build as build_fifo
from build_gx8002_uart_interrupt import build as build_interrupt
from link_gx8002_irq import link as build_irq
from build_gx8002_irq_entry_candidate import build as build_entry
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha
from verify_gx8002_memcpy_source import decode


def build(include_initialize=False):
    inputs={'configure':build_configure(),'fifo':build_fifo(),'interrupt':build_interrupt(),'irq':build_irq(),'entry':build_entry()}
    from analyze_gx8002_uart_descriptor_defaults import analyze
    inputs['uart_defaults']=analyze()
    out=ROOT/('build/gx8002-uart-initialize-source' if include_initialize else 'build/gx8002-uart-configure-source');out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    storage=ROOT/'components/shared/gx8002/runtime_gx8002_irq_storage.c';storage_obj=out/'irq_storage.o'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(storage),'-o',str(storage_obj)],check=True)
    uart_storage=ROOT/'components/shared/gx8002/runtime_gx8002_uart_storage.c';uart_obj=out/'uart_storage.o'
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I'+str(sdk/'arch/soc/grus/include'),'-c',str(uart_storage),'-o',str(uart_obj)],check=True)
    runtime=Path(inputs['configure']['runtime_link']['archive'])
    objects=[ROOT/'build/gx8002-uart-configure/configure.o',ROOT/'build/gx8002-uart-fifo-depth/control.o',ROOT/'build/gx8002-uart-interrupt/control.o',ROOT/'build/gx8002-irq/irq.o',ROOT/'build/gx8002-irq/entry.o',ROOT/'build/gx8002-irq/body.o',storage_obj,uart_obj]
    if include_initialize:
        from build_gx8002_uart_initialize import build as build_initialize
        from build_gx8002_platform_gate_candidate import build as build_gate
        from build_gx8002_clock_frequency_candidate import build as build_frequency
        from build_gx8002_clock_divider_candidate import build as build_divider
        inputs.update(initialize=build_initialize(),gate=build_gate(),frequency=build_frequency(),divider=build_divider())
        objects.extend([ROOT/'build/gx8002-uart-initialize/control.o',ROOT/'build/gx8002-platform-gate/gate.o',ROOT/'build/gx8002-clock-frequency/frequency.o',ROOT/'build/gx8002-board/clock-divider-candidate.o'])
    from build_gx8002_uart_receive_control import build as build_receive_control
    from build_gx8002_uart_transmit_control import build as build_transmit_control
    inputs.update(receive_control=build_receive_control(),transmit_control=build_transmit_control())
    objects.extend([ROOT/'build/gx8002-uart-receive-control/control.o',ROOT/'build/gx8002-uart-transmit-control/control.o'])
    from build_gx8002_uart_flush import build as build_flush
    inputs['flush']=build_flush()
    objects.append(ROOT/'build/gx8002-uart-flush/control.o')
    from build_gx8002_uart_receive_byte import build as build_receive_byte
    inputs['receive_byte']=build_receive_byte()
    objects.append(ROOT/'build/gx8002-uart-receive-byte/control.o')
    from build_gx8002_uart_read import build as build_read
    inputs['read']=build_read()
    objects.append(ROOT/'build/gx8002-uart-read/control.o')
    from build_gx8002_uart_write import build as build_write
    from link_gx8002_uart_console import build as build_console
    inputs.update(write=build_write(),console=build_console())
    # Keep the source transmitter section; console wrappers have separate state.
    tx_script=out/'transmitter.ld'
    tx_script.write_text('SECTIONS { .text.open_cfw_gx8002_uart_transmit : { *(.text.open_cfw_gx8002_uart_transmit) } /DISCARD/ : { *(.text*) } }\n')
    tx_obj=out/'transmitter.o'
    subprocess.run([pre+'ld','-r','-T',str(tx_script),str(ROOT/'build/gx8002-uart-console/console-size.o'),'-o',str(tx_obj)],check=True)
    objects.extend([ROOT/'build/gx8002-uart-write/control.o',tx_obj])
    script=out/'uart.ld';script.write_text('SECTIONS { .text 0x10340000 : { *(.text*) } .rodata : { *(.rodata*) } .data 0x20080000 : { *(.data*) } .bss 0x20090000 (NOLOAD) : { *(.bss*) *(COMMON) } }\n')
    linked=out/'uart.elf';subprocess.run([pre+'ld','-T',str(script),*[str(p) for p in objects],str(runtime),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));symbols={s['name']:s for s in elf.symbols() if s['name']}
    if any(s['section']==0 for s in symbols.values()):raise ValueError('Unresolved UART cluster symbol')
    if any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('Unapplied UART cluster relocation')
    funcs=('uart_configure','uart_fifo_depth','uart_interrupt','request_irq','irq_enable','irq_entry','irq_dispatch_body')
    funcs+=('uart_receive_start','uart_receive_stop','uart_transmit_start','uart_transmit_stop')
    funcs+=('uart_flush','uart_receive_byte','uart_read','uart_write','uart_transmit')
    if include_initialize:funcs+=('uart_initialize','platform_gate','clock_frequency','clock_divider')
    for name in funcs:
        sym=symbols['open_cfw_gx8002_'+name]
        if sym['section']>=len(elf.sections) or not sym['size']:raise ValueError(('UART function not source-owned',name))
    for name in ('uart_receive_start','uart_receive_stop','uart_transmit_start','uart_transmit_stop'):
        sym=symbols['open_cfw_gx8002_'+name]
        dis_control=decode(subprocess.check_output([pre+'objdump','-d','--start-address='+hex(sym['value']),'--stop-address='+hex(sym['value']+sym['size']),str(linked)],text=True))
        calls_control={int(args,0) for op,args,width in dis_control.values() if op=='bsr'}
        if calls_control!={symbols['open_cfw_gx8002_irq_save']['value'],symbols['open_cfw_gx8002_irq_restore']['value']}:raise ValueError('UART control IRQ relocation')
    uart_symbol=symbols['open_cfw_gx8002_uart_descriptors'];uart_data=elf.sections[uart_symbol['section']]
    if uart_symbol['size']!=256 or uart_data['name']!='.data':raise ValueError('UART descriptor ownership')
    from analyze_gx8002_upstream_objects import IMAGE
    offset=uart_symbol['value']-uart_data['address']
    if elf.contents(uart_data)[offset:offset+256]!=IMAGE.read_bytes()[0x18aa8:0x18ba8]:raise ValueError('Source UART defaults differ')
    bss=next(s for s in elf.sections if s['name']=='.bss')
    for name,size in (('irq_table',256),('irq_saved_enable',8)):
        sym=symbols['open_cfw_gx8002_'+name]
        if sym['section']!=bss['index'] or sym['size']!=size or bss['type']!=8:raise ValueError('IRQ storage ownership')
    dis=subprocess.check_output([pre+'objdump','-d',str(linked)],text=True);(out/'uart.disassembly.txt').write_text(dis);code=decode(dis)
    config=symbols['open_cfw_gx8002_uart_configure'];calls={int(args,0) for pc,(op,args,width) in code.items() if config['value']<=pc<config['value']+config['size'] and op=='bsr'}
    for name in ('uart_fifo_depth','request_irq'):
        if symbols['open_cfw_gx8002_'+name]['value'] not in calls:raise ValueError('UART relocated helper call')
    text=next(s for s in elf.sections if s['name']=='.text')
    literals={int(args.split(',')[1].strip(),0) for pc,(op,args,width) in code.items() if config['value']<=pc<config['value']+config['size'] and op=='lrw'}
    if symbols['open_cfw_gx8002_uart_interrupt']['value'] not in literals:raise ValueError('UART handler pointer relocation')
    return {'inputs':inputs,'uart_storage_source_sha256':sha(uart_storage.read_bytes()),'uart_descriptor_address':uart_symbol['value'],'uart_descriptor_bytes':uart_symbol['size'],'irq_storage_source_sha256':sha(storage.read_bytes()),'linked_sha256':sha(linked.read_bytes()),'text_bytes':text['size'],'bss_bytes':bss['size'],'function_addresses':{name:symbols['open_cfw_gx8002_'+name]['value'] for name in funcs},'unresolved_symbols':[],'source_admitted':False,'hardware_qualified':False,'limits':['Source-linked analysis cluster, not firmware image. Relocated instruction execution, startup BSS zeroing and physical placement remain unqualified. Source-authored UART defaults match stock; relocated descriptor consumers remain to be composed; upstream libgcc finite UART corpus only, not full IEEE qualification.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-uart-configure-source-link.json').write_text(json.dumps(r,indent=2)+'\n');print('Source UART cluster text:',r['text_bytes'],'BSS:',r['bss_bytes'])
