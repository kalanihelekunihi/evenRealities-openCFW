# SPDX-License-Identifier: MIT
"""Link reconstructed DMA/UART sources together; analysis ELF, not firmware."""
import json,subprocess,struct
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

SOURCES=('irq','dma_initialize','dma_irq_handler','dma_bus_address','dma_callback','dma_clear','dma_configure','dma_deallocate','dma_descriptors','dma_release','dma_select','dma_transfer','uart_dma_burst','uart_receive_buffer','uart_receive_complete','uart_receive_control','uart_receive_dma','dcache_clean_range','dcache_invalid_range','dcache_clean_invalid_range','uart_transmit_dma','uart_transmit_complete','uart_transmit_buffer','uart_flush')

def build(callback_address=0x20027320,owned_dma=False,owned_irq=False,owned_uart=False):
    out=ROOT/'build/gx8002-dma-uart-source';out.mkdir(parents=True,exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';header='include/driver/gx_dma_ahb.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+header],text=True).strip();authenticated_blob(sdk/header,blob)
    from verify_gx8002_csi_source import HEADERS
    upstream=[]
    for name in (*HEADERS,'LICENSE','include/driver/gx_irq.h'):
        identity=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        upstream.append({'path':name,'git_blob':identity,'sha256':sha(authenticated_blob(sdk/name,identity))})
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');objects=[];sources=[]
    for name in SOURCES+(('dma_storage',) if owned_dma else ())+(('irq_storage',) if owned_irq else ())+(('uart_storage',) if owned_uart else ()):
        source=ROOT/('components/shared/gx8002/runtime_gx8002_'+name+'.c');obj=out/(name+'.o')
        extra=['-fno-tree-scev-cprop'] if name=='dma_descriptors' else ['--param=max-completely-peel-times=0'] if name=='dma_irq_handler' else ['-fno-shrink-wrap'] if name=='irq' else []
        includes=[]
        if name=='uart_storage':includes+=['-I'+str(sdk/'arch/soc/grus/include')]
        if name=='irq':
            for directory in ('arch/soc/grus/include','include/utility','include/utility/libc'):includes+=['-isystem',str(sdk/directory)]
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],*extra,*includes,'-I'+str(sdk/'include/driver'),'-c',str(source),'-o',str(obj)],check=True)
        objects.append(str(obj));sources.append({'name':name,'sha256':sha(source.read_bytes()),'extra_flags':extra})
    from build_gx8002_platform_gate_candidate import build as build_gate
    clock_dependency=build_gate()
    objects.append(str(ROOT/'build/gx8002-platform-gate/gate.o'))
    sources.append({'name':'platform_gate','sha256':clock_dependency['source_sha256'],'extra_flags':clock_dependency['flags']})
    aliases={'open_cfw_gx8002_dma_resource':'open_cfw_gx8002_platform_gate','open_cfw_gx8002_uart_dma_cache':'open_cfw_gx8002_dcache_invalid_range','open_cfw_gx8002_dma_descriptor_cache':'open_cfw_gx8002_dcache_clean_range','open_cfw_gx8002_dma_complete_cache':'open_cfw_gx8002_dcache_clean_invalid_range'}
    external={'open_cfw_gx8002_irq_table':0x20026ef4,'open_cfw_gx8002_irq_saved_enable':0x20026eec,'open_cfw_gx8002_dma_callbacks':callback_address,'open_cfw_gx8002_dma_state':0x2002e93c,'open_cfw_gx8002_uart_descriptors':0x20026a94}
    if owned_uart:del external['open_cfw_gx8002_uart_descriptors']
    if owned_dma:
        del external['open_cfw_gx8002_dma_callbacks']
        del external['open_cfw_gx8002_dma_state']
    if owned_irq:
        del external['open_cfw_gx8002_irq_table']
        del external['open_cfw_gx8002_irq_saved_enable']
    script=out/'analysis.ld';script.write_text('SECTIONS { .text 0x10310000 : { *(.text*) } .rodata : { *(.rodata*) } .data 0x20080000 : { *(.data*) } .bss 0x20090000 (NOLOAD) : { *(.bss*) } }\n'+''.join(f'{a} = {b};\n' for a,b in aliases.items())+''.join(f'{a} = {b:#x};\n' for a,b in external.items()))
    target=out/'dma-uart.elf';subprocess.run([pre+'ld','-T',str(script),*objects,'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));undefined=[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]
    if undefined:raise ValueError(('Unresolved symbols',undefined))
    rows=[]
    for sec in elf.sections:
        if sec['name'] in ('.text','.rodata','.data'):
            if elf.relocations(sec['index']):raise ValueError('Unresolved relocations')
            data=elf.contents(sec);rows.append({'name':sec['name'],'address':sec['address'],'bytes':len(data),'sha256':sha(data)})
    symbols={s['name']:s for s in elf.symbols() if s['name']}
    for name in ('open_cfw_gx8002_platform_gate','__module_get_info'):
        if symbols[name]['section']!=next(s['index'] for s in elf.sections if s['name']=='.text'):raise ValueError('Clock function is not source text')
    owned_uart_storage=[]
    if owned_uart:
        from analyze_gx8002_uart_descriptor_defaults import analyze
        analyze()
        from analyze_gx8002_upstream_objects import IMAGE
        symbol=symbols['open_cfw_gx8002_uart_descriptors'];section=elf.sections[symbol['section']]
        offset=symbol['value']-section['address']
        if symbol['size']!=256 or section['name']!='.data':raise ValueError('UART source storage extent')
        if elf.contents(section)[offset:offset+256]!=IMAGE.read_bytes()[0x18aa8:0x18ba8]:raise ValueError('UART source defaults')
        owned_uart_storage.append({'symbol':symbol['name'],'address':symbol['value'],'bytes':256,'compiled_defaults_verified':True})
    owned_storage=[]
    if owned_dma:
        bss=next(s for s in elf.sections if s['name']=='.bss')
        for name,size in (('dma_state',884),('dma_callbacks',16)):
            symbol=symbols['open_cfw_gx8002_'+name]
            if symbol['section']!=bss['index'] or symbol['size']!=size or bss['type']!=8:raise ValueError('DMA storage extent/type')
            owned_storage.append({'symbol':symbol['name'],'address':symbol['value'],'bytes':size,'zero_initialized':True})
        state_address=symbols['open_cfw_gx8002_dma_state']['value']
        for index,offset in enumerate((23,455)):
            address=(state_address+offset)&~15
            low=state_address+8+432*index
            if not low<=address or address+416>low+432:raise ValueError('Descriptor list exceeds source storage')
        callback_address=symbols['open_cfw_gx8002_dma_callbacks']['value']
    owned_irq_storage=[]
    if owned_irq:
        bss=next(s for s in elf.sections if s['name']=='.bss')
        for name,size in (('irq_table',256),('irq_saved_enable',8)):
            symbol=symbols['open_cfw_gx8002_'+name]
            if symbol['section']!=bss['index'] or symbol['size']!=size or bss['type']!=8:raise ValueError('IRQ storage extent/type')
            owned_irq_storage.append({'symbol':symbol['name'],'address':symbol['value'],'bytes':size,'zero_initialized':True})
    linked_irq={}
    for name in ('request_irq','irq_save','irq_restore','irq_enable'):
        symbol=symbols['open_cfw_gx8002_'+name]
        if symbol['section']!=next(s['index'] for s in elf.sections if s['name']=='.text'):raise ValueError('IRQ function is not source text')
        linked_irq[name]=symbol['value']
    completion=symbols['open_cfw_gx8002_uart_receive_complete']['value']
    receive=symbols['open_cfw_gx8002_uart_receive_dma']
    sec=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(sec)
    start=receive['value']-sec['address'];body=payload[start:start+receive['size']+8]
    relocation_text=subprocess.check_output([pre+'objdump','-r',str(out/'uart_receive_dma.o')],text=True)
    if 'R_CKCORE_ADDR32   open_cfw_gx8002_uart_receive_complete' not in relocation_text:raise ValueError('Missing callback relocation')
    if completion==0x102030e4 or struct.pack('<I',completion) not in body or struct.pack('<I',0x102030e4) in body:raise ValueError('Callback did not relocate')
    state_relocations=[]
    for unit,symbol in (('dma_clear','dma_state'),('dma_select','dma_state'),('uart_receive_control','uart_descriptors')):
        relocation=subprocess.check_output([pre+'objdump','-r',str(out/(unit+'.o'))],text=True)
        if 'open_cfw_gx8002_'+symbol not in relocation:raise ValueError(('Missing state relocation',unit))
        state_relocations.append({'unit':unit,'symbol':'open_cfw_gx8002_'+symbol})
    callback_storage=[]
    for name in ('dma_callback','dma_irq_handler'):
        relocation=subprocess.check_output([pre+'objdump','-r',str(out/(name+'.o'))],text=True)
        if 'R_CKCORE_ADDR32   open_cfw_gx8002_dma_callbacks' not in relocation:raise ValueError('Callback storage lacks symbol relocation')
        symbol=symbols['open_cfw_gx8002_'+name];start=symbol['value']-sec['address']
        body=payload[start:start+symbol['size']+8]
        if struct.pack('<I',callback_address) not in body:raise ValueError('Callback storage did not relocate')
        if callback_address!=0x20027320 and struct.pack('<I',0x20027320) in body:raise ValueError('Stale callback address')
        callback_storage.append({'function':name,'address':callback_address})
    initializer=symbols['open_cfw_gx8002_dma_initialize']
    start=initializer['value']-sec['address']
    body=payload[start:start+initializer['size']+8]
    handler=symbols['open_cfw_gx8002_dma_irq_handler']['value']
    initializer_relocations=subprocess.check_output([pre+'objdump','-r',str(out/'dma_initialize.o')],text=True)
    if 'R_CKCORE_ADDR32   open_cfw_gx8002_dma_irq_handler' not in initializer_relocations or struct.pack('<I',handler) not in body:raise ValueError('DMA IRQ handler pointer did not relocate')
    from verify_gx8002_memcpy_source import decode
    disassembly=subprocess.check_output([pre+'objdump','-d',str(target)],text=True)
    decoded=decode(disassembly)
    transmit_calls=[]
    for caller,callees in (
        ('uart_transmit_dma',('dcache_clean_range','dma_select','uart_dma_burst','dma_callback','dma_transfer','dma_release')),
        ('uart_transmit_complete',('dma_release','uart_flush')),
        ('uart_transmit_buffer',('uart_transmit_dma','irq_save','irq_restore'))):
        symbol=symbols['open_cfw_gx8002_'+caller]
        targets={int(args,0) for pc,(op,args,width) in decoded.items() if symbol['value']<=pc<symbol['value']+symbol['size'] and op=='bsr'}
        wanted={symbols['open_cfw_gx8002_'+name]['value'] for name in callees}
        if targets!=wanted:raise ValueError(('Transmit source helper closure',caller))
        transmit_calls.append({'caller':caller,'callees':list(callees)})
    tx=symbols['open_cfw_gx8002_uart_transmit_dma'];tx_complete=symbols['open_cfw_gx8002_uart_transmit_complete']['value']
    literals={int(args.split(',')[1],0) for pc,(op,args,width) in decoded.items() if tx['value']<=pc<tx['value']+tx['size'] and op=='lrw'}
    if tx_complete not in literals or 0x102030c4 in literals:raise ValueError('Transmit completion relocation')
    calls=[]
    for caller,callee in (('dma_initialize','request_irq'),('dma_select','irq_save'),('dma_select','irq_restore'),('dma_deallocate','irq_save'),('dma_deallocate','irq_restore')):
        symbol=symbols['open_cfw_gx8002_'+caller]
        targets=[int(args,0) for pc,(op,args,width) in decoded.items() if symbol['value']<=pc<symbol['value']+symbol['size'] and op=='bsr']
        if linked_irq[callee] not in targets:raise ValueError(('IRQ source call missing',caller,callee))
        calls.append({'caller':caller,'callee':callee,'target':linked_irq[callee]})
    clock_calls=[]
    gate_address=symbols['open_cfw_gx8002_platform_gate']['value']
    for name in ('dma_initialize','dma_select','dma_deallocate'):
        symbol=symbols['open_cfw_gx8002_'+name]
        targets=[int(args,0) for pc,(op,args,width) in decoded.items() if symbol['value']<=pc<symbol['value']+symbol['size'] and op=='bsr']
        if gate_address not in targets:raise ValueError(('Clock source call missing',name))
        clock_calls.append({'caller':name,'target':gate_address})
    callback_link={'symbol':'open_cfw_gx8002_uart_receive_complete','linked_address':completion,'original_address':0x102030e4,'symbol_relocation_verified':True}
    (out/'dma-uart.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    return {'owned_uart_storage':owned_uart_storage,'transmit_source_calls':transmit_calls,'transmit_completion_address':tx_complete,'owned_dma_storage':owned_storage,'owned_irq_storage':owned_irq_storage,'clock_dependency':clock_dependency,'upstream_dependencies':upstream,'linked_irq':linked_irq,'sdk_commit':SDK_COMMIT,'header_blob':blob,'sources':sources,'source_count':len(sources),'sections':rows,'callback_link':callback_link,'callback_storage':callback_storage,'state_relocations':state_relocations,'dma_irq_handler_pointer':handler,'irq_source_calls':calls,'clock_source_calls':clock_calls,'source_aliases':aliases,'external_bindings':external,'unresolved_symbols':undefined,'source_admitted':False,'firmware_image':False,'hardware_qualified':False,'limits':['Analysis-only relocated link; receive completion callback is symbol-relocated and checked. IRQ registration/masking use reconstructed C with pinned upstream CSI; clock uses pinned upstream GRUS source and tables; persistent state remains externally bound. Full integration/type compatibility and hardware initialization remain unproved.']}

if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-dma-uart-source-link.json').write_text(json.dumps(report,indent=2)+'\n');print('Linked source units:',report['source_count'],'sections:',report['sections'])
