#!/usr/bin/env python3
"""Verify typed native initialization and execute its real provider tables."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    from verify_native_gatt import DESCRIPTORS as GATT_DESCRIPTORS
    from verify_native_bae8_send import DESCRIPTORS
    bae8_sections=''.join('.r1.bae8.log.'+name+' '+hex(address)+' : { *(.r1.bae8.log.'+name+') } ' for name,address in DESCRIPTORS.items())
    observer_layout=json.loads((BASE/'sdk-ble-dispatch/report.json').read_text())['layout'];observer_data_sections=[('.sdh_ble_observers'+str(i),int(pair[0],16)) for i,pair in enumerate(observer_layout['ranges']) if i]+[('.rodata.sdh_ble_observers_array',0x9ca70),('.rodata.sdh_ble_observers',0x9ca94)]
    observer_ld_sections=''.join(name+' '+hex(address)+' : { *('+name+') } ' for name,address in observer_data_sections)
    receipt=BASE/'board/verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'board/report.json').read_text());obj=BASE/'board/native-board.o';assert sha(obj)==report['relocatable_sha256']
    for path,digest in report['objects'].items():assert sha(ROOT/path)==digest,path
    for path,digest in report['input_reports'].items():assert sha(BASE/path)==digest,path
    roots={**{'r1_stock_i2c'+str(i+2)+'_register':a for i,a in enumerate((0x56508,0x56520,0x56538,0x56550))},'r1_named_gpio_register_all':0x54c24,'r1_named_adc_register_all':0x5493c,'r1_i2c5_nfc_resource_registration':0x50464,'r1_native_named_wdt_register':0x56694}
    comparisons=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin';data=tmp/'records.bin'
        lifecycle_configuration=BASE/'native-task-lifecycle/configuration-evidence.json';task_rows=json.loads(lifecycle_configuration.read_text())['rows']
        data_anchors=report.get('unresolved_data_anchors',{})
        startup_sections=' .bss.m_stack_is_enabled 0x20007a1b (NOLOAD) : { *(.bss.m_stack_is_enabled) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } .r1.ble.semaphores 0x200064fc (NOLOAD) : { *(.r1.ble.semaphores) } .bss.ucMaxSysCallPriority 0x20007810 (NOLOAD) : { *(.bss.ucMaxSysCallPriority) } .bss.uxCriticalNesting 0x20007814 (NOLOAD) : { *(.bss.uxCriticalNesting) } .bss.ulMaxPRIGROUPValue 0x20007818 (NOLOAD) : { *(.bss.ulMaxPRIGROUPValue) } .bss.xTickCount 0x20007828 (NOLOAD) : { *(.bss.xTickCount) } .bss.xSchedulerRunning 0x20007830 (NOLOAD) : { *(.bss.xSchedulerRunning) } .bss.uxSchedulerSuspended 0x20007850 (NOLOAD) : { *(.bss.uxSchedulerSuspended) } .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .bss.m_state 0x20007948 (NOLOAD) : { *(.bss.m_state) } .bss.m_alloc_index 0x20007949 (NOLOAD) : { *(.bss.m_alloc_index) } .bss.m_wdt_event_handler 0x2000794c (NOLOAD) : { *(.bss.m_wdt_event_handler) }  .r1.watchdog.fault_record 0x20006734 (NOLOAD) : { *(.r1.watchdog.fault_record) } .r1.watchdog.mutex_storage 0x20015414 (NOLOAD) : { *(.r1.watchdog.mutex_storage) } .r1.watchdog.mutex_attributes 0x993c0 : { *(.r1.watchdog.mutex_attributes) } .r1.watchdog.port 0x993d0 : { *(.r1.watchdog.port) } .r1.watchdog.device 0x20007694 (NOLOAD) : { *(.r1.watchdog.device) } .r1.wdt.state 0x20007630 : { *(.r1.wdt.state) } '
        watchdog_sections_extra=' .r1.watchdog.enabled 0x20006730 (NOLOAD) : { *(.r1.watchdog.enabled) } .r1.watchdog.mutex 0x20006738 (NOLOAD) : { *(.r1.watchdog.mutex) } .r1.watchdog.registry 0x20015404 (NOLOAD) : { *(.r1.watchdog.registry) } .bss.pxCurrentTCB 0x2000781c (NOLOAD) : { *(.bss.pxCurrentTCB) } '
        watchdog_slots={'gtx':0x200065b8,'msgtx':0x200065b4,'sensor':0x20006604,'service':0x20006688,'storage':0x200066d4}
        watchdog_sections=' .r1.sync.flags 0x2000655c (NOLOAD) : { *(.r1.sync.flags) } '+''.join(' .r1.task.'+name+'.watchdog '+hex(address)+' (NOLOAD) : { *(.r1.task.'+name+'.watchdog) } ' for name,address in watchdog_slots.items())
        task_sections=''.join(' .r1.task.'+row['letter']+'.'+suffix+' '+row[key]+' (NOLOAD) : { *(.r1.task.'+row['letter']+'.'+suffix+') } ' for row in task_rows for suffix,key in (('tcb','control_block'),('stack','stack')))
        qwr_sections=''.join('.r1.qwr.'+letter+' '+hex(0x20007e40+i*12)+' (NOLOAD) : { *(.r1.qwr.'+letter+') } ' for i,letter in enumerate('abc'))
        gatt_log_sections=''.join('.r1.gatt.log.'+n+' '+hex(a)+' : { *(.r1.gatt.log.'+n+') } ' for n,a in GATT_DESCRIPTORS.items())
        ld.write_text('SECTIONS { '+'.r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } '+gatt_log_sections+'.r1.gatt.context 0x20007e1c (NOLOAD) : { *(.r1.gatt.context) } '+qwr_sections+observer_ld_sections+'.sdh_ble_observers0 0xc4568 : { *(.sdh_ble_observers0) } '+bae8_sections+'.r1.output.ring 0x44fec : { *(.r1.output.ring) } .r1.output.sdk 0x4501c : { *(.r1.output.sdk) } .wdt.log.init 0x7b5f8 : { *(.rodata.nrfx_wdt_init.r1_log_format) } .wdt.log.alloc 0x7b4e4 : { *(.rodata.nrfx_wdt_channel_alloc.r1_log_format) } .wdt.log.enable 0x7b560 : { *(.rodata.nrfx_wdt_enable.r1_log_format) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } .r1.tx.channel1 0x200065bc : { *(.r1.tx.channel1) } .r1.tx.shared 0x200065e0 : { *(.r1.tx.shared) } .r1.connection.field6 0x200064b8 : { *(.r1.connection.field6) } .r1.event.sensor 0x2000668c : { *(.r1.event.sensor) } .r1.event.system 0x20006608 : { *(.r1.event.system) } .r1.event.storage 0x200066d8 : { *(.r1.event.storage) } .r1.log.cache 0x200068f4 : { *(.r1.log.cache) } .r1.log.cache_buffer 0x20016bc8 (NOLOAD) : { *(.r1.log.cache_buffer) } .r1.log.export_buffer 0x20018bc8 (NOLOAD) : { *(.r1.log.export_buffer) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .r1.i2c5.state 0x20006838 : { *(.r1.i2c5.state) } .r1.vnfc.adc 0x20006854 (NOLOAD) : { *(.r1.vnfc.adc) } .r1.log.clock 0x2000653c (NOLOAD) : { *(.r1.log.clock) } .r1.log.export 0x20006906 (NOLOAD) : { *(.r1.log.export) } .r1.log.level 0x200068ed : { *(.r1.log.level) } .r1.log.sequence 0x200068ee (NOLOAD) : { *(.r1.log.sequence) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .r1.adc.state 0x20006ef4 : { *(.r1.adc.state) } .r1.adc.ops 0x20006f70 : { *(.r1.adc.ops) } .r1.gpio.records 0x200070c0 : { *(.r1.gpio.records) } .r1.gpio.ops 0x200071f4 : { *(.r1.gpio.ops) } .r1.twi.records 0x20007400 : { *(.r1.twi.records) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } '+task_sections+watchdog_sections+watchdog_sections_extra+startup_sections+' .bss 0x20020000 (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],*['--undefined='+n for n in ('r1_native_watchdog_initialize','r1_native_watchdog_check','r1_native_watchdog_expired_task','r1_native_output_worker','r1_native_ble_send_phone','r1_native_ble_send_glasses','r1_native_ble_message_send','r1_ble_error_is_benign','r1_ble_flush_one','r1_ble_flush_bounded','r1_ble_flush_drain','r1_ble_link_semaphore','r1_ble_semaphore_take','r1_native_bae8_send','r1_native_sd_ble_gatts_hvx','blcm_link_ctx_get','ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init','r1_sdk_connection_event','conn_handle_list_get','nrf_atflags_set','nrf_atflags_clear','nrf_atomic_u32_and','nrf_atomic_u32_or','r1_sdk_connection_observer','r1_sdk_ble_events_poll','nrf_section_iter_init','nrf_section_iter_next','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3','nrf_ble_qwr_on_ble_evt','nrf_ble_qwr_init','r1_sdk_qwr_user_mem_reply','nrf_ble_gatt_init','r1_sdk_gatt_link_init','nrf_ble_gatt_on_ble_evt','r1_gatt_on_mtu_request','r1_gatt_data_length_update','ble_advertising_on_ble_evt','ble_advertising_start','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set','r1_sdk_adv_flags_set','r1_sdk_adv_phy_is_valid','r1_sdk_adv_use_whitelist','ble_advdata_parse','ble_advdata_search','ble_advertising_init','ble_advdata_encode','r1_sdk_adv_data_size_max_get')],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(n for n in report['remaining_symbols'] if n not in data_anchors)],*['--defsym='+n+'='+a for n,a in data_anchors.items()],str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.twi.records='+str(data),str(elf)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        tick_variables={'ucMaxSysCallPriority':(0x20007810,1),'uxCriticalNesting':(0x20007814,4),'ulMaxPRIGROUPValue':(0x20007818,4),'xTickCount':(0x20007828,4),'xSchedulerRunning':(0x20007830,4),'uxSchedulerSuspended':(0x20007850,4)}
        for name,(address,size) in tick_variables.items():assert syms[name]==address
        for name in ('r1_native_output_worker','r1_native_ble_send_phone','r1_native_ble_send_glasses','r1_native_ble_message_send','r1_ble_error_is_benign','r1_ble_flush_one','r1_ble_flush_bounded','r1_ble_flush_drain','r1_ble_link_semaphore','r1_ble_semaphore_take','r1_native_bae8_send','r1_native_sd_ble_gatts_hvx','blcm_link_ctx_get','ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init','r1_sdk_connection_event','conn_handle_list_get','nrf_atflags_set','nrf_atflags_clear','nrf_atomic_u32_and','nrf_atomic_u32_or','r1_sdk_connection_observer','r1_sdk_ble_events_poll','nrf_section_iter_init','nrf_section_iter_next','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3','nrf_ble_qwr_on_ble_evt','nrf_ble_qwr_init','r1_sdk_qwr_user_mem_reply','nrf_ble_gatt_init','r1_sdk_gatt_link_init','nrf_ble_gatt_on_ble_evt','r1_gatt_on_mtu_request','r1_gatt_data_length_update','ble_advertising_on_ble_evt','ble_advertising_start','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set','r1_sdk_adv_flags_set','r1_sdk_adv_phy_is_valid','r1_sdk_adv_use_whitelist','ble_advdata_parse','ble_advdata_search','ble_advertising_init','ble_advdata_encode','r1_sdk_adv_data_size_max_get'):assert name in syms
        assert syms['r1_native_bae8_context_get']==syms['blcm_link_ctx_get']
        assert syms['r1_sdk_ble_stack_enabled']==0x20007a1b and syms['r1_sdk_ble_observer_sections']==0x9ca70 and syms['r1_sdk_ble_observer_set']==0x9ca94
        for i,letter in enumerate('abc'):assert syms['r1_ble_qwr_context_'+letter]==0x20007e40+i*12
        assert syms['r1_ble_advertising_context_a']==0x20007e64 and syms['r1_ble_advertising_context_b']==0x200082b0
        assert syms['r1_ble_gatt_context']==0x20007e1c
        assert syms['r1_sdk_connection_observer']==0xc4568
        assert syms['m_bcs']==0x2002bdb0
        assert syms['r1_ble_link_semaphores']==0x200064fc
        assert syms['nrf_nvic_state']==0x2002c2fc
        assert (syms['m_state'],syms['m_alloc_index'],syms['m_wdt_event_handler'])==(0x20007948,0x20007949,0x2000794c)
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        for address,size in tick_variables.values():assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
        for address in (0x20007e64,0x200082b0):assert bytes(stock.mem_read(address,1076))==bytes(candidate.mem_read(address,1076))==bytes(1076)
        assert bytes(stock.mem_read(0x20007e1c,36))==bytes(candidate.mem_read(0x20007e1c,36))==bytes(36)
        assert bytes(stock.mem_read(0x20007e40,36))==bytes(candidate.mem_read(0x20007e40,36))==bytes(36)
        assert bytes(stock.mem_read(0x20007a1b,1))==bytes(candidate.mem_read(0x20007a1b,1))==bytes(1)
        assert bytes(stock.mem_read(0x2002bdb0,124))==bytes(candidate.mem_read(0x2002bdb0,124))==bytes(124)
        assert bytes(stock.mem_read(0x200064fc,8))==bytes(candidate.mem_read(0x200064fc,8))==bytes(8)
        assert bytes(stock.mem_read(0x2002c2fc,12))==bytes(candidate.mem_read(0x2002c2fc,12))==bytes(12)
        candidate.mem_map(0x90000,0x10000);candidate.mem_map(0x70000,0x10000);candidate.mem_map(0x40000,0x10000);candidate.mem_map(0x50000,0x10000);candidate.mem_map(0xb0000,0x10000);candidate.mem_map(0xc0000,0x10000);candidate.mem_write(0x1000000,text.read_bytes())
        bae8_descriptor_bytes=0;gatt_descriptor_bytes=0
        for index,(section,address) in enumerate(tuple(('.r1.gatt.log.'+n,a) for n,a in GATT_DESCRIPTORS.items())+tuple(observer_data_sections)+(('.sdh_ble_observers0',0xc4568),)+tuple(('.r1.bae8.log.'+n,a) for n,a in DESCRIPTORS.items())+(( '.r1.output.ring',0x44fec),('.r1.output.sdk',0x4501c),( '.wdt.log.init',0x7b5f8),('.wdt.log.alloc',0x7b4e4),('.wdt.log.enable',0x7b560),('.r1.watchdog.port',0x993d0),('.r1.watchdog.mutex_attributes',0x993c0),('.r1.wdt.state',0x20007630),('.r1.connection.field8',0x200064ba),('.r1.connection.field10',0x200064bc),('.r1.tx.channel1',0x200065bc),('.r1.tx.shared',0x200065e0),('.r1.connection.field6',0x200064b8),('.r1.event.sensor',0x2000668c),('.r1.event.system',0x20006608),('.r1.event.storage',0x200066d8),('.r1.log.cache',0x200068f4),('.r1.log.level',0x200068ed),('.r1.log.mode',0x200068ec),('.r1.i2c5.state',0x20006838),('.r1.adc.state',0x20006ef4),('.r1.adc.ops',0x20006f70),('.r1.gpio.records',0x200070c0),('.r1.gpio.ops',0x200071f4),('.r1.twi.records',0x20007400))):
            path=tmp/(str(index)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);candidate.mem_write(address,path.read_bytes())
            if section.startswith('.r1.gatt.log.'):gatt_descriptor_bytes+=len(path.read_bytes())
            if section.startswith('.r1.bae8.log.'):bae8_descriptor_bytes+=len(path.read_bytes())
            if section.startswith(('.r1.gatt.log.','.wdt.log.','.r1.output.','.r1.bae8.log.')):assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
        for row in observer_layout['records']:
            address=int(row['address'],16);context_address=int(observer_layout['contexts'][row['context']],16) if row['context'] else 0
            assert struct.unpack('<2I',bytes(stock.mem_read(address,8)))==(int(observer_layout['handlers'][row['handler']],16)|1,context_address)
            assert struct.unpack('<2I',bytes(candidate.mem_read(address,8)))==((syms[row['handler']]|1),context_address)
        assert bytes(stock.mem_read(0x9ca70,32))==bytes(candidate.mem_read(0x9ca70,32)) and bytes(stock.mem_read(0x9ca94,12))==bytes(candidate.mem_read(0x9ca94,12))
        assert struct.unpack('<2I',bytes(stock.mem_read(0xc4568,8)))==(0x5380d,0)
        assert struct.unpack('<2I',bytes(candidate.mem_read(0xc4568,8)))==((syms['r1_sdk_connection_event']|1),0)
        assert bytes(stock.mem_read(0x200064b8,6))==bytes(candidate.mem_read(0x200064b8,6))==b'\xff'*6
        context_layouts=((0x2000668c,'a','668c',0x43b8d,0x43b75),(0x20006608,'f','6608',0x46925,0x4690d),(0x200066d8,'g','66d8',0x46a45,0x46a2d),(0x200065e0,'b','65e0',0x44ef1,0x44ed9),(0x200065bc,'e','65bc',0x4509d,0x45085))
        for address,letter,stop_id,create,stop in context_layouts:
            original=struct.unpack('<4I',bytes(stock.mem_read(address,16)));compiled=struct.unpack('<4I',bytes(candidate.mem_read(address,16)));assert original==(create,stop,0,0);assert compiled==((syms['r1_thread_create_'+letter]|1),(syms['r1_task_stop_'+stop_id]|1),0,0)
        for row in task_rows:
            for key,size in (('control_block',112),('stack',row['stack_bytes'])):
                address=int(row[key],16);assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
        assert bytes(stock.mem_read(0x200068f4,16))==bytes(candidate.mem_read(0x200068f4,16))==struct.pack('<4I',0x20016bc8,8192,0,0)
        for address,length in ((0x20016bc8,8192),(0x20018bc8,236)):
            assert bytes(stock.mem_read(address,length))==bytes(candidate.mem_read(address,length))==bytes(length)
        for address in [0x2000655c,*watchdog_slots.values()]:
            assert bytes(stock.mem_read(address,4))==bytes(candidate.mem_read(address,4))==bytes(4)
        for address,length in ((0x20006730,1),(0x20006738,4),(0x20015404,16),(0x2000781c,4)):
            assert bytes(stock.mem_read(address,length))==bytes(candidate.mem_read(address,length))==bytes(length)
        for address,length in ((0x20006734,4),(0x20015414,80),(0x20007694,4),(0x20007948,8)):
            assert bytes(stock.mem_read(address,length))==bytes(candidate.mem_read(address,length))==bytes(length)
        original_wdt=bytearray(stock.mem_read(0x20007630,80));compiled_wdt=bytearray(candidate.mem_read(0x20007630,80))
        for offset,original,name in ((44,0x56659,'r1_native_named_wdt_open'),(68,0x56639,'r1_native_named_wdt_feed')):
            assert struct.unpack_from('<I',original_wdt,offset)[0]==original and struct.unpack_from('<I',compiled_wdt,offset)[0]==syms[name]|1
        for offset in (0,44,68):original_wdt[offset:offset+4]=compiled_wdt[offset:offset+4]=bytes(4)
        assert original_wdt==compiled_wdt
        original_port=struct.unpack('<3I',bytes(stock.mem_read(0x993d0,12)));compiled_port=struct.unpack('<3I',bytes(candidate.mem_read(0x993d0,12)));assert original_port==(0x66265,0x66235,0x6623f);assert compiled_port==tuple(syms[name]|1 for name in ('r1_native_watchdog_port_start','r1_native_watchdog_port_stop','r1_native_watchdog_port_sample'))
        from unicorn import UC_HOOK_CODE
        def trap(uc,address,size,data):
            if 0x100e000<=address<=0x100e5ff:raise AssertionError('Unresolved production seam invoked')
        candidate.hook_add(UC_HOOK_CODE,trap)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
        baseline={id(uc):bytes(uc.mem_read(0x20000000,0x40000)) for uc in (stock,candidate)}
        def registry(uc):
            result=[];pointer=struct.unpack('<I',bytes(uc.mem_read(0x20007680,4)))[0]
            while pointer:
                assert len(result)<15
                name,ops=struct.unpack('<2I',bytes(uc.mem_read(pointer,8)));text_name=bytes(uc.mem_read(name,64)).split(b'\0')[0].decode();result.append((pointer,text_name,ops));pointer=struct.unpack('<I',bytes(uc.mem_read(pointer+20,4)))[0]
            return result
        def compare(name):
            nonlocal comparisons
            results=[]
            for uc,entry in ((stock,roots[name]),(candidate,syms[name])):
                events[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                uc.emu_start(entry|1,0x20000100,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                results.append((None if name=='r1_i2c5_nfc_resource_registration' else uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),registry(uc),bytes(uc.mem_read(0x20006838,32))))
            assert results[0]==results[1],(name,results);comparisons+=1
        import itertools
        groups=[['r1_native_named_wdt_register'],['r1_named_adc_register_all'],['r1_named_gpio_register_all'],['r1_stock_i2c'+str(i)+'_register' for i in range(2,6)]]
        for order in itertools.permutations(groups):
            for uc in (stock,candidate):uc.mem_write(0x20000000,baseline[id(uc)]);uc.mem_write(0x50000000,bytes(4096))
            for group in order:
                for name in group:compare(name)
            assert len(registry(candidate))==15
            for _ in range(2):compare('r1_i2c5_nfc_resource_registration')
            assert struct.unpack('<2I',bytes(candidate.mem_read(0x20006838,8)))==(0x200071ac,0x20007584)
            assert struct.unpack('<I',bytes(candidate.mem_read(0x20006854,4)))[0]==0x20006f58
            # Clearing the registry retains lazy GPO/bus handles but clears refreshed ADC.
            for uc in (stock,candidate):uc.mem_write(0x20007680,bytes(4))
            compare('r1_i2c5_nfc_resource_registration')
            assert struct.unpack('<I',bytes(candidate.mem_read(0x20006854,4)))[0]==0
    result=dict(application_sha256=sha(app),board_report_sha256=sha(BASE/'board/report.json'),relocatable_sha256=sha(obj),binary_runtime_linked=False,cache_initialization_bytes_compared=8444,event_context_prefix_initial_bytes_compared=48,tx_context_prefix_initial_bytes_compared=32,task_zero_initial_bytes_compared=28208,connection_initial_bytes_compared=6,sync_watchdog_initial_bytes_compared=24,watchdog_registry_current_task_initial_bytes_compared=25,watchdog_startup_initial_zero_bytes_compared=88,wdt_sdk_initial_control_bytes_compared=8,nvic_initial_zero_bytes_compared=12,watchdog_log_descriptor_bytes_compared=87,output_descriptor_bytes_compared=68,ble_semaphore_initial_zero_bytes_compared=8,connection_state_candidate_initial_zero_bytes_compared=124,registry_observer_record_bytes_pointer_normalized=8,ble_observer_table_bytes_pointer_normalized=96,ble_observer_range_set_bytes_compared=44,gatt_log_descriptor_bytes_compared=gatt_descriptor_bytes,advertising_compatible_context_zero_bytes_compared=2152,gatt_context_initial_zero_bytes_compared=36,qwr_context_initial_zero_bytes_compared=36,ble_stack_initial_zero_bytes_compared=1,bae8_descriptor_bytes_compared=bae8_descriptor_bytes,rtos_tick_critical_initial_zero_bytes_compared=21,watchdog_device_state_bytes_compared=80,watchdog_port_table_bytes_compared=12,comparisons=comparisons,registry_records=15,registration_group_orders=24,resolved_handles={'nfc_gpo_irq':'0x200071ac','i2c_5':'0x20007584','vnfc_rect_adc':'0x20006f58'},scope='Actual source-owned WDT/ADC/GPIO/TWI records populate one registry; original versus compiled registration/discovery match across all group orders without prebound handles',test_only_bindings=['Unresolved function providers are test-only traps; dispatch tables, BAE8 service and opaque observer contexts are address-only bindings without initial content/extent proof'],limitations=['Structured/Nordic logging backends remain explicit production requirements.','All memory/string code in this executable comes from compiled, attributable C providers; original Arm runtime identity remains unproven.','This does not establish complete application startup, hardware behavior or instruction identity.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{comparisons} native board comparisons passed across 24 registration orders; all three NFC handles resolve from 15 real records')
if __name__=='__main__':main()
