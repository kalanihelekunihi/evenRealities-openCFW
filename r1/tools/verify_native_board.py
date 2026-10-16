#!/usr/bin/env python3
"""Verify typed native initialization and execute its real provider tables."""
import hashlib,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    from verify_native_advertising_configuration import DESCRIPTORS as ADVERTISING_DESCRIPTORS
    module_config=json.loads((BASE/'sdk-log-modules/configuration-evidence.json').read_text());module_sections='.r1.log.modules 0xc441c : { *(.r1.log.modules) } '+''.join('.r1.log.module_name.'+str(row['index'])+' '+row['name_address']+' : { *(.r1.log.module_name.'+str(row['index'])+') } ' for row in module_config['rows'])
    from verify_sdk_segger_rtt import FIELDS as SEGGER_FIELDS,SECTIONS as SEGGER_SECTIONS
    segger_sections=''.join(n+' '+hex(a)+(' (NOLOAD)' if n not in ('.r1.rtt.terminal','.r1.rtt.identifier') else '')+' : { *('+n+') } ' for n,a in SEGGER_SECTIONS.items())
    from verify_sdk_rtt_backend import FIELDS as RTT_FIELDS,SECTIONS as RTT_SECTIONS,ENTRIES as RTT_ENTRIES
    RTT_FIELDS={n:v for n,v in RTT_FIELDS.items() if n!="r1_sdk_logger_data"}
    rtt_sections="".join(".bss."+n+" "+hex(a)+" (NOLOAD) : { *(.bss."+n+") } " for n,(a,z) in RTT_FIELDS.items())+"".join(n+" "+hex(a)+" : { *("+n+") } " for n,a in RTT_SECTIONS.items())
    from verify_sdk_logger_initialization import INIT_FIELDS,INIT_SECTIONS
    from verify_sdk_logger_frontend import FIELDS as LOGGER_FIELDS,SECTIONS as LOGGER_SECTIONS
    LOGGER_FIELDS={**LOGGER_FIELDS,**INIT_FIELDS};LOGGER_SECTIONS={**LOGGER_SECTIONS,**INIT_SECTIONS}
    logger_sections="".join(".bss."+n+" "+hex(a)+" (NOLOAD) : { *(.bss."+n+") } " for n,(a,z) in LOGGER_FIELDS.items())+"".join(n+" "+hex(a)+" : { *("+n+") } " for n,a in LOGGER_SECTIONS.items())
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
        from verify_native_thread_init_logs import DESCRIPTORS as THREAD_LOG_DESCRIPTORS
        thread_log_sections=''.join('.r1.thread_init_log.'+n+' '+hex(a)+' : { *(.r1.thread_init_log.'+n+') } ' for n,a in THREAD_LOG_DESCRIPTORS.items())
        from verify_native_delayed_initialize import RAM as DELAYED_RAM
        delayed_sections=''.join('.r1.delayed.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.delayed.'+n+') } ' for n,(a,z) in DELAYED_RAM.items())
        from verify_rtos_scheduler_start import SECTIONS as STARTUP_SECTIONS
        startup_sections+=' .bss.prvSampleTimeNow.xLastTime 0x20007864 (NOLOAD) : { *(.bss.prvSampleTimeNow.xLastTime) } '+''.join(n+' '+hex(a)+' (NOLOAD) : { *('+n+') } ' for n,a in STARTUP_SECTIONS.items())
        watchdog_sections_extra=' .r1.watchdog.enabled 0x20006730 (NOLOAD) : { *(.r1.watchdog.enabled) } .r1.watchdog.mutex 0x20006738 (NOLOAD) : { *(.r1.watchdog.mutex) } .r1.watchdog.registry 0x20015404 (NOLOAD) : { *(.r1.watchdog.registry) } .bss.pxCurrentTCB 0x2000781c (NOLOAD) : { *(.bss.pxCurrentTCB) } '
        watchdog_slots={'gtx':0x200065b8,'msgtx':0x200065b4,'sensor':0x20006604,'service':0x20006688,'storage':0x200066d4}
        watchdog_sections=' .r1.sync.flags 0x2000655c (NOLOAD) : { *(.r1.sync.flags) } '+''.join(' .r1.task.'+name+'.watchdog '+hex(address)+' (NOLOAD) : { *(.r1.task.'+name+'.watchdog) } ' for name,address in watchdog_slots.items())
        task_sections=''.join(' .r1.task.'+row['letter']+'.'+suffix+' '+row[key]+' (NOLOAD) : { *(.r1.task.'+row['letter']+'.'+suffix+') } ' for row in task_rows for suffix,key in (('tcb','control_block'),('stack','stack')))
        qwr_sections=''.join('.r1.qwr.'+letter+' '+hex(0x20007e40+i*12)+' (NOLOAD) : { *(.r1.qwr.'+letter+') } ' for i,letter in enumerate('abc'))
        gatt_log_sections=''.join('.r1.gatt.log.'+n+' '+hex(a)+' : { *(.r1.gatt.log.'+n+') } ' for n,a in GATT_DESCRIPTORS.items())
        from verify_native_kv_store_get import STRINGS as KV_GET_STRINGS
        kv_get_sections=''.join('.r1.kv.get.log.'+n+' '+hex(a)+' : { *(.r1.kv.get.log.'+n+') } ' for n,a in KV_GET_STRINGS.items())
        from verify_native_kv_store_put import STRINGS as KV_PUT_STRINGS
        kv_put_sections=''.join('.r1.kv.put.log.'+n+' '+hex(a)+' : { *(.r1.kv.put.log.'+n+') } ' for n,a in KV_PUT_STRINGS.items())
        from verify_native_kv_initialize import STRINGS as KV_INIT_STRINGS,FIELDS as KV_INIT_FIELDS
        kv_init_sections=''.join('.r1.kv.init.log.'+n+' '+hex(a)+' : { *(.r1.kv.init.log.'+n+') } ' for n,a in KV_INIT_STRINGS.items())+''.join('.r1.kv.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.kv.'+n+') } ' for n,(a,z) in KV_INIT_FIELDS.items())+'.r1.kv.mutex_attributes 0x9a0e8 : { *(.r1.kv.mutex_attributes) } '
        from verify_native_kv_scans import STRINGS as KV_SCAN_STRINGS
        kv_scan_sections=''.join('.r1.kv.scan.log.'+n+' '+hex(a)+' : { *(.r1.kv.scan.log.'+n+') } ' for n,a in KV_SCAN_STRINGS.items())
        from verify_sdk_fal_partition import FIELDS as FAL_PARTITION_FIELDS
        fal_partition_sections=''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FAL_PARTITION_FIELDS.items())+'.rodata.r1_fal_partition_records 0x9c250 : { *(.rodata.r1_fal_partition_records) } '
        from verify_native_fal_device import FIELDS as NATIVE_FAL_FIELDS,ENTRIES as NATIVE_FAL_ENTRIES
        native_fal_sections=''.join('.r1.fal.'+n+' '+hex(a)+' (NOLOAD) : { *(.r1.fal.'+n+') } ' for n,(a,z) in NATIVE_FAL_FIELDS.items())+'.r1.fal.device_record 0x200077c4 : { *(.r1.fal.device_record) } '
        internal_flash_sections='.r1.flash.pending 0x20006f96 (NOLOAD) : { *(.r1.flash.pending) } .r1.flash.name 0xc06d4 : { *(.r1.flash.name) } .r1.flash.record 0x20006f98 : { *(.r1.flash.record) } .r1.flash.fstorage 0x20007dc0 : { *(.r1.flash.fstorage) } '
        from verify_sdk_fstorage_sd import FIELDS as SD_FSTORAGE_FIELDS,API as SD_FSTORAGE_API,OBSERVERS as SD_FSTORAGE_OBSERVERS
        sd_fstorage_sections='.r1.fstorage_sd.fifo_pointer 0x9c85c : { *(.r1.fstorage_sd.fifo_pointer) } '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in SD_FSTORAGE_FIELDS.items())+'.rodata.r1_sdk_fstorage_sd_flash_info 0x9c860 : { *(.rodata.r1_sdk_fstorage_sd_flash_info) } .rodata.nrf_fstorage_sd 0x9c86c : { *(.rodata.nrf_fstorage_sd) } '+''.join('.sdh_'+n+'_observers0 '+hex(a)+' : { *(.sdh_'+n+'_observers0) } ' for n,(a,h) in SD_FSTORAGE_OBSERVERS.items())
        sdh_sections={'.rodata.sdh_req_observers_array':0x9ca18,'.rodata.sdh_req_observers':0x9ca2c,'.rodata.sdh_state_observers_array':0x9ca50,'.rodata.sdh_state_observers':0x9ca38,'.rodata.sdh_stack_observers_array':0x9ca60,'.rodata.sdh_stack_observers':0x9ca44,'.r1.sdh.stack.records':0xc45e8,'.r1.sdh.state.records':0xc45f8}
        soc_sections={'.rodata.sdh_soc_observers_array':0x9caa0,'.rodata.sdh_soc_observers':0x9cab0,'.r1.soc.observer0':0xc45d0,'.sdh_soc_observers1':0xc45e0}
        soc_ld=''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in soc_sections.items())
        sdh_ld=''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in sdh_sections.items())+''.join('.bss.'+n+' '+hex(0x20007a18+i)+' (NOLOAD) : { *(.bss.'+n+') } ' for i,n in enumerate(('m_nrf_sdh_enabled','m_nrf_sdh_suspended','m_nrf_sdh_continue')))
        from verify_sdk_power_management import FIELDS as POWER_FIELDS
        power_sections=''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in POWER_FIELDS.items())
        from verify_rtos_scheduler_resume import FIELDS as SCHEDULER_FIELDS
        from verify_rtos_scheduler_tick import FIELDS as TICK_FIELDS,OWNED as TICK_OWNED
        SCHEDULER_FIELDS={**SCHEDULER_FIELDS,**{n:v for n,v in TICK_FIELDS.items() if n in TICK_OWNED},'xSuspendedTaskList':(0x2002b244,20),'uxTaskNumber':(0x20007840,4),'xTasksWaitingTermination':(0x2002b230,20),'uxDeletedTasksWaitingCleanUp':(0x20007820,4)}
        scheduler_sections='.r1.scheduler.top_used_priority 0x2000784c : { *(.data.uxTopUsedPriority) *(.rodata.uxTopUsedPriority) } '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in SCHEDULER_FIELDS.items() if n not in ('uxSchedulerSuspended','pxCurrentTCB'))
        ld.write_text('SECTIONS { '+'.r1.stacmd.failed_transactions 0x200075c0 : { *(.r1.stacmd.failed_transactions) } .r1.stacmd_retry.ring 0x3570c : { *(.r1.stacmd_retry.ring) } .r1.stacmd_retry.sdk 0x3573c : { *(.r1.stacmd_retry.sdk) } '+thread_log_sections+delayed_sections+'.r1.stack_overflow.ring 0x95c44 : { *(.r1.stack_overflow.ring) } .r1.stack_overflow.nordic 0x95c70 : { *(.r1.stack_overflow.nordic) } .r1.application.initial_sp 0x27000 : { *(.r1.application.initial_sp) } .r1.application.svc_vector 0x2702c : { *(.r1.application.svc_vector) } .r1.application.pendsv_vector 0x27038 : { *(.r1.application.pendsv_vector) } .r1.task.initial_xpsr 0x9c4cc : { *(.r1.task.initial_xpsr) } '+scheduler_sections+'.r1.heap.state 0x200077fc (NOLOAD) : { *(.r1.heap.state) } .r1.heap.storage 0x2001e588 (NOLOAD) : { *(.r1.heap.storage) } .r1.heap.start 0x2002ad88 (NOLOAD) : { *(.r1.heap.start) } .r1.output_gpio.configuration 0x20007228 : { *(.r1.output_gpio.configuration) } .r1.stacmd.configuration 0x200075c4 : { *(.r1.stacmd.configuration) } .r1.output_gpio.name0 0xc0754 : { *(.r1.output_gpio.name0) } .r1.output_gpio.name1 0xc0770 : { *(.r1.output_gpio.name1) } .r1.output_gpio.name2 0xc0780 : { *(.r1.output_gpio.name2) } .r1.output_gpio.name3 0xc0760 : { *(.r1.output_gpio.name3) } .r1.output_gpio.name4 0xc0790 : { *(.r1.output_gpio.name4) } .r1.stacmd.name 0xc07c8 : { *(.r1.stacmd.name) } .r1.hw_twi.primary 0x20006fe8 : { *(.r1.hw_twi.primary) } .r1.hw_twi.secondary 0x20007054 : { *(.r1.hw_twi.secondary) } .r1.hw_twi.name0 0xc06e4 : { *(.r1.hw_twi.name0) } .r1.hw_twi.name1 0xc06ec : { *(.r1.hw_twi.name1) } .r1.init.devices 0xc4534 : { *(.r1.init.devices) } .r1.rtc.lookup.name 0x50dd8 : { *(.r1.rtc.lookup.name) } .r1.rtc.irq36.vector 0x270d0 : { *(.r1.rtc.irq36.vector) } .r1.rtc.error.ring 0x4e604 : { *(.r1.rtc.error.ring) } .r1.rtc.error.nordic 0x4e630 : { *(.r1.rtc.error.nordic) } .bss.r1_sdk_rtc_control 0x20007950 (NOLOAD) : { *(.bss.r1_sdk_rtc_control) } .bss.r1_sdk_rtc_handlers 0x20007954 (NOLOAD) : { *(.bss.r1_sdk_rtc_handlers) } .r1.rtc.log.enabled 0x7ad5c : { *(.r1.rtc.log.enabled) } .r1.rtc.log.tick 0x7ae90 : { *(.r1.rtc.log.tick) } .r1.rtc.log.function 0x7ae28 : { *(.r1.rtc.log.function) } .r1.rtc.tm 0x20037e88 (NOLOAD) : { *(.r1.rtc.tm) } .r1.rtc.months 0xbdb18 : { *(.r1.rtc.months) } .r1.rtc.ops 0x200073dc : { *(.r1.rtc.ops) } .r1.rtc.defaults 0x9a638 : { *(.r1.rtc.defaults) } .r1.rtc.counter 0x2000737c (NOLOAD) : { *(.r1.rtc.counter) } .r1.rtc.record 0x20007384 : { *(.r1.rtc.record) } .r1.rtc.name 0xc07a0 : { *(.r1.rtc.name) } .r1.clock.backend 0x99c8c : { *(.r1.clock.backend) } .r1.clock.defaults 0x99c54 : { *(.r1.clock.defaults) } '+module_sections+'.data.m_colors 0x200079f4 : { *(.data.m_colors) } '+segger_sections+rtt_sections+logger_sections+power_sections+'.r1.clock.irq0.vector 0x27040 : { *(.r1.clock.irq0.vector) } .bss.r1_sdk_nrfx_clock_control 0x20007938 (NOLOAD) : { *(.bss.r1_sdk_nrfx_clock_control) } .bss.r1_sdk_clock_control 0x2002c154 (NOLOAD) : { *(.bss.r1_sdk_clock_control) } '+soc_ld+sdh_ld+sd_fstorage_sections+internal_flash_sections+native_fal_sections+fal_partition_sections+kv_scan_sections+'.bss.r1_fal_device_initialized 0x200077b2 (NOLOAD) : { *(.bss.r1_fal_device_initialized) } .bss.r1_fal_initialized 0x200077b1 (NOLOAD) : { *(.bss.r1_fal_initialized) } '+kv_init_sections+kv_put_sections+kv_get_sections+'.r1.kv.port_record 0x20006984 : { *(.r1.kv.port_record) } .r1.kv.port_slot 0x20006974 (NOLOAD) : { *(.r1.kv.port_slot) } .r1.kv.mutex 0x20006978 (NOLOAD) : { *(.r1.kv.mutex) } .r1.kv.block_cursor 0x20019e49 (NOLOAD) : { *(.r1.kv.block_cursor) } '+''.join('.r1.advertising.log.'+n+' '+hex(a)+' : { *(.r1.advertising.log.'+n+') } ' for n,a in ADVERTISING_DESCRIPTORS.items())+'.r1.advertising.intervals 0x99114 : { *(.r1.advertising.intervals) } .r1.advertising.product_payload 0x20007e04 (NOLOAD) : { *(.r1.advertising.product_payload) } '+'.r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } '+gatt_log_sections+'.r1.gatt.context 0x20007e1c (NOLOAD) : { *(.r1.gatt.context) } '+qwr_sections+observer_ld_sections+'.sdh_ble_observers0 0xc4568 : { *(.sdh_ble_observers0) } '+bae8_sections+'.r1.output.ring 0x44fec : { *(.r1.output.ring) } .r1.output.sdk 0x4501c : { *(.r1.output.sdk) } .wdt.log.init 0x7b5f8 : { *(.rodata.nrfx_wdt_init.r1_log_format) } .wdt.log.alloc 0x7b4e4 : { *(.rodata.nrfx_wdt_channel_alloc.r1_log_format) } .wdt.log.enable 0x7b560 : { *(.rodata.nrfx_wdt_enable.r1_log_format) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } .r1.tx.channel1 0x200065bc : { *(.r1.tx.channel1) } .r1.tx.shared 0x200065e0 : { *(.r1.tx.shared) } .r1.connection.field6 0x200064b8 : { *(.r1.connection.field6) } .r1.event.sensor 0x2000668c : { *(.r1.event.sensor) } .r1.event.system 0x20006608 : { *(.r1.event.system) } .r1.event.storage 0x200066d8 : { *(.r1.event.storage) } .r1.log.cache 0x200068f4 : { *(.r1.log.cache) } .r1.log.cache_buffer 0x20016bc8 (NOLOAD) : { *(.r1.log.cache_buffer) } .r1.log.export_buffer 0x20018bc8 (NOLOAD) : { *(.r1.log.export_buffer) } .r1.time.registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) } .r1.time.rtc 0x20007690 (NOLOAD) : { *(.r1.time.rtc) } .r1.time.state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) } .r1.i2c5.state 0x20006838 : { *(.r1.i2c5.state) } .r1.vnfc.adc 0x20006854 (NOLOAD) : { *(.r1.vnfc.adc) } .r1.log.clock 0x2000653c (NOLOAD) : { *(.r1.log.clock) } .r1.log.export 0x20006906 (NOLOAD) : { *(.r1.log.export) } .r1.log.level 0x200068ed : { *(.r1.log.level) } .r1.log.sequence 0x200068ee (NOLOAD) : { *(.r1.log.sequence) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .r1.adc.state 0x20006ef4 : { *(.r1.adc.state) } .r1.adc.ops 0x20006f70 : { *(.r1.adc.ops) } .r1.gpio.records 0x200070c0 : { *(.r1.gpio.records) } .r1.gpio.ops 0x200071f4 : { *(.r1.gpio.ops) } .r1.twi.records 0x20007400 : { *(.r1.twi.records) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } '+task_sections+watchdog_sections+watchdog_sections_extra+startup_sections+' .bss 0x2003e000 (NOLOAD) : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],*['--undefined='+n for n in ('osThreadFlagsSet','osThreadFlagsWait','osEventFlagsSet','osDelay','vTaskRemoveFromUnorderedEventList','xTimerPendFunctionCallFromISR','vEventGroupSetBitsCallback','osMutexNew','osMutexAcquire','osMutexRelease','osSemaphoreAcquire','osSemaphoreRelease','osSemaphoreGetCount','xTaskPriorityInherit','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueGetCount','osMessageQueueGetCapacity','r1_native_timer_task','xTimerCreate','xTimerCreateStatic','xTimerGenericCommand','xQueueGenericSendFromISR','xQueueReceive','vQueueWaitForMessageRestricted','vTaskPlaceOnEventListRestricted','uxTaskGetNumberOfTasks','vApplicationStackOverflowHook','vPortStartFirstTask','SVC_Handler','PendSV_Handler','vTaskSwitchContext','__isr_vector','r1_application_svc_vector','r1_application_pendsv_vector','xPortStartScheduler','vPortSetupTimerInterrupt','vTaskStartScheduler','xTimerCreateTimerTask','r1_native_timer_infrastructure','vApplicationGetIdleTaskMemory','vApplicationGetTimerTaskMemory','eTaskConfirmSleepModeStatus','vTaskStepTick','r1_native_idle_task','r1_native_expected_idle_time','r1_native_task_idle_cleanup','r1_native_task_initialize','r1_native_task_create','r1_native_task_create_static','r1_native_initial_xpsr','uxTopUsedPriority','xDelayedTaskList1','xDelayedTaskList2','r1_module_init_table_run','r1_module_post_init_run','r1_native_boot_initcall_dispatch','r1_device_initcalls','r1_stock_dispatch_08','r1_native_rtc_cached_device','RTC2_IRQHandler','r1_sdk_rtc_irq_dispatch','r1_rtc_irq36_vector','r1_native_rtc_gmtime','r1_native_rtc_epoch_to_calendar','r1_native_rtc_tick','r1_native_rtc_epoch_initialize','r1_native_rtc_open','r1_native_rtc_register','r1_rtc_boot_defaults','r1_rtc_device_ops','r1_native_rtc_snapshot','r1_native_rtc_calendar_write','r1_native_rtc_callback_bind','r1_native_watchdog_initialize','r1_native_watchdog_check','r1_native_watchdog_expired_task','r1_native_output_worker','r1_native_ble_send_phone','r1_native_ble_send_glasses','r1_native_ble_message_send','r1_ble_error_is_benign','r1_ble_flush_one','r1_ble_flush_bounded','r1_ble_flush_drain','r1_ble_link_semaphore','r1_ble_semaphore_take','r1_native_bae8_send','r1_native_sd_ble_gatts_hvx','blcm_link_ctx_get','ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init','r1_sdk_connection_event','conn_handle_list_get','nrf_atflags_set','nrf_atflags_clear','nrf_atomic_u32_and','nrf_atomic_u32_or','r1_sdk_connection_observer','r1_sdk_ble_events_poll','nrf_section_iter_init','nrf_section_iter_next','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3','nrf_ble_qwr_on_ble_evt','nrf_ble_qwr_init','r1_sdk_qwr_user_mem_reply','nrf_ble_gatt_init','r1_sdk_gatt_link_init','nrf_ble_gatt_on_ble_evt','r1_gatt_on_mtu_request','r1_gatt_data_length_update','ble_advertising_on_ble_evt','ble_advertising_start','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set','r1_sdk_adv_flags_set','r1_sdk_adv_phy_is_valid','r1_sdk_adv_use_whitelist','ble_advdata_parse','ble_advdata_search','ble_advertising_init','ble_advdata_encode','r1_sdk_adv_data_size_max_get','r1_nordic_advertising_configuration','r1_advertising_params_init','r1_advertising_configuration_byte_get','r1_advertising_product_sn_read','r1_advertising_event_plan_build','r1_advertising_status_publish','r1_advertising_connection_intervals','r1_kv_class_read','r1_kv_class_write','r1_health_record_read','r1_health_record_write','r1_kv_port_bind','r1_kv_port_lock','r1_kv_port_unlock','r1_kv_port_control','r1_kv_port_zero_4','r1_kv_port_zero_8','r1_kv_port_zero_12','r1_kv_store_get','r1_kv_store_put','r1_kv_port_initialize','r1_fal_is_initialized','fal_init_check','fal_init','fal_flash_init','fal_flash_device_find','fal_partition_init','fal_partition_find','r1_native_fal_device_initialize','r1_native_fal_device_read','r1_native_fal_device_write','r1_native_fal_device_erase','r1_internal_flash_callback_configuration','r1_internal_flash_erase_and_geometry_control','r1_internal_flash_fstorage_configuration','r1_internal_flash_device_read','r1_internal_flash_device_registration','r1_internal_flash_device_write','r1_internal_flash_page_erase','r1_internal_flash_mapped_read','r1_internal_flash_word_write','r1_internal_flash_wait','r1_internal_flash_event_handler','nrf_fstorage_init','nrf_fstorage_erase','nrf_fstorage_write','nrf_fstorage_is_busy','nrf_fstorage_sd','nrf_fstorage_sys_evt_handler','nrf_fstorage_sdh_req_handler','nrf_fstorage_sdh_state_handler','r1_sdk_fstorage_sd_sys_obs','r1_sdk_fstorage_sd_req_obs','r1_sdk_fstorage_sd_state_obs','r1_sdk_fstorage_sd_fifo_pointer','nrf_atfifo_clear','nrf_atfifo_init','nrf_atfifo_item_alloc','nrf_atfifo_item_free','nrf_atfifo_item_get','nrf_atfifo_item_put','nrf_atfifo_wspace_req','nrf_atfifo_wspace_close','nrf_atfifo_rspace_req','nrf_atfifo_rspace_close','nrf_atfifo_space_clear','nrf_atomic_flag_set_fetch','nrf_atomic_u32_fetch_or','r1_clock_initialize','r1_clock_backend_snapshot','r1_clock_backend_bind','r1_clock_second_changed','r1_clock_default_backend_get','r1_clock_default_backend','r1_clock_boot_defaults','r1_rtt_delay_cycles','r1_log_local_datetime_fill','r1_log_module_records','nrf_log_color_id_get','nrf_fprintf','nrf_fprintf_fmt','nrf_fprintf_buffer_flush','nrf_log_std_entry_process','nrf_log_hexdump_entry_process','r1_log_prefix_process','nrf_log_backend_serial_put','SEGGER_RTT_Init','SEGGER_RTT_WriteNoLock','nrf_log_default_backends_init','nrf_log_backend_rtt_init','nrf_log_backend_rtt_api','nrf_log_init','nrf_log_backend_add','nrf_ringbuf_init','nrf_log_panic','nrf_log_frontend_dequeue','nrf_log_frontend_std_0','nrf_log_frontend_std_1','nrf_log_frontend_std_2','nrf_log_frontend_std_3','nrf_log_frontend_std_4','nrf_log_frontend_std_5','nrf_log_frontend_std_6','nrf_log_frontend_hexdump','r1_sdh_state_observer_567ac','nrf_pwr_mgmt_shutdown','r1_sdk_power_shutdown_process','nrf_atomic_u32_fetch_store','r1_power_log_marker','r1_power_system_reset','POWER_CLOCK_IRQHandler','r1_power_clock_irq0_vector','nrfx_clock_init','nrfx_clock_enable','nrfx_clock_lfclk_start','nrfx_clock_lfclk_stop','r1_soc_observer_907fc','r1_sdh_state_observer_890f0','r1_sdk_clock_notify','r1_sdk_clock_irq_handler','r1_sdk_clock_item_enqueue','nrf_drv_clock_init','nrf_drv_clock_lfclk_request','nrf_drv_clock_lfclk_release','r1_clock_log_info','r1_sdk_soc_events_poll','r1_soc_observer_priority0','r1_soc_observer_priority1','nrf_sdh_is_enabled','nrf_sdh_evts_poll','nrf_sdh_request_continue','nrf_sdh_enable_request','nrf_sdh_disable_request','r1_sdh_stack_observers','r1_sdh_native_state_observers','strncmp','r1_kv_flash_erase_scan','r1_latest_valid_flash_slot_scan_adapter')],*['--defsym='+n+'='+hex(0x1100001+i*16) for i,n in enumerate(n for n in report['remaining_symbols'] if n not in data_anchors)],*['--defsym='+n+'='+a for n,a in data_anchors.items()],*['--undefined='+n for n in ['r1_native_delayed_initialize', 'r1_native_delayed_worker', 'r1_native_delayed_schedule', 'r1_native_delayed_push', 'r1_native_delayed_reschedule', 'r1_native_delayed_cancel', 'osTimerNew', 'osTimerStart', 'osTimerStop', 'pvTimerGetTimerID', 'xTimerIsTimerActive', 'r1_delayed_queue_attributes', 'r1_delayed_thread_attributes', 'r1_delayed_mutex_attributes', 'r1_delayed_timer_attributes']],*['--undefined='+n for n in ('r1_native_service_hardware_initialize','r1_native_storage_hardware_initialize')],str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.twi.records='+str(data),str(elf)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        tick_variables={'ucMaxSysCallPriority':(0x20007810,1),'uxCriticalNesting':(0x20007814,4),'ulMaxPRIGROUPValue':(0x20007818,4),'xTickCount':(0x20007828,4),'xSchedulerRunning':(0x20007830,4),'uxSchedulerSuspended':(0x20007850,4)}
        for name,(address,size) in tick_variables.items():assert syms[name]==address
        for name in ('r1_native_output_worker','r1_native_ble_send_phone','r1_native_ble_send_glasses','r1_native_ble_message_send','r1_ble_error_is_benign','r1_ble_flush_one','r1_ble_flush_bounded','r1_ble_flush_drain','r1_ble_link_semaphore','r1_ble_semaphore_take','r1_native_bae8_send','r1_native_sd_ble_gatts_hvx','blcm_link_ctx_get','ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init','r1_sdk_connection_event','conn_handle_list_get','nrf_atflags_set','nrf_atflags_clear','nrf_atomic_u32_and','nrf_atomic_u32_or','r1_sdk_connection_observer','r1_sdk_ble_events_poll','nrf_section_iter_init','nrf_section_iter_next','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3','nrf_ble_qwr_on_ble_evt','nrf_ble_qwr_init','r1_sdk_qwr_user_mem_reply','nrf_ble_gatt_init','r1_sdk_gatt_link_init','nrf_ble_gatt_on_ble_evt','r1_gatt_on_mtu_request','r1_gatt_data_length_update','ble_advertising_on_ble_evt','ble_advertising_start','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set','r1_sdk_adv_flags_set','r1_sdk_adv_phy_is_valid','r1_sdk_adv_use_whitelist','ble_advdata_parse','ble_advdata_search','ble_advertising_init','ble_advdata_encode','r1_sdk_adv_data_size_max_get','r1_nordic_advertising_configuration','r1_advertising_params_init','r1_advertising_configuration_byte_get','r1_advertising_product_sn_read','r1_advertising_event_plan_build','r1_advertising_status_publish','r1_advertising_connection_intervals','r1_kv_class_read','r1_kv_class_write','r1_health_record_read','r1_health_record_write','r1_kv_port_bind','r1_kv_port_lock','r1_kv_port_unlock','r1_kv_port_control','r1_kv_port_zero_4','r1_kv_port_zero_8','r1_kv_port_zero_12','r1_kv_store_get','r1_kv_store_put','r1_kv_port_initialize','r1_fal_is_initialized','fal_init_check','fal_init','fal_flash_init','fal_flash_device_find','fal_partition_init','fal_partition_find','r1_native_fal_device_initialize','r1_native_fal_device_read','r1_native_fal_device_write','r1_native_fal_device_erase','r1_internal_flash_callback_configuration','r1_internal_flash_erase_and_geometry_control','r1_internal_flash_fstorage_configuration','r1_internal_flash_device_read','r1_internal_flash_device_registration','r1_internal_flash_device_write','r1_internal_flash_page_erase','r1_internal_flash_mapped_read','r1_internal_flash_word_write','r1_internal_flash_wait','r1_internal_flash_event_handler','nrf_fstorage_init','nrf_fstorage_erase','nrf_fstorage_write','nrf_fstorage_is_busy','nrf_fstorage_sd','nrf_fstorage_sys_evt_handler','nrf_fstorage_sdh_req_handler','nrf_fstorage_sdh_state_handler','r1_sdk_fstorage_sd_sys_obs','r1_sdk_fstorage_sd_req_obs','r1_sdk_fstorage_sd_state_obs','r1_sdk_fstorage_sd_fifo_pointer','nrf_atfifo_clear','nrf_atfifo_init','nrf_atfifo_item_alloc','nrf_atfifo_item_free','nrf_atfifo_item_get','nrf_atfifo_item_put','nrf_atfifo_wspace_req','nrf_atfifo_wspace_close','nrf_atfifo_rspace_req','nrf_atfifo_rspace_close','nrf_atfifo_space_clear','nrf_atomic_flag_set_fetch','nrf_atomic_u32_fetch_or','r1_clock_initialize','r1_clock_backend_snapshot','r1_clock_backend_bind','r1_clock_second_changed','r1_clock_default_backend_get','r1_clock_default_backend','r1_clock_boot_defaults','r1_rtt_delay_cycles','r1_log_local_datetime_fill','r1_log_module_records','nrf_log_color_id_get','nrf_fprintf','nrf_fprintf_fmt','nrf_fprintf_buffer_flush','nrf_log_std_entry_process','nrf_log_hexdump_entry_process','r1_log_prefix_process','nrf_log_backend_serial_put','SEGGER_RTT_Init','SEGGER_RTT_WriteNoLock','nrf_log_default_backends_init','nrf_log_backend_rtt_init','nrf_log_backend_rtt_api','nrf_log_init','nrf_log_backend_add','nrf_ringbuf_init','nrf_log_panic','nrf_log_frontend_dequeue','nrf_log_frontend_std_0','nrf_log_frontend_std_1','nrf_log_frontend_std_2','nrf_log_frontend_std_3','nrf_log_frontend_std_4','nrf_log_frontend_std_5','nrf_log_frontend_std_6','nrf_log_frontend_hexdump','r1_sdh_state_observer_567ac','nrf_pwr_mgmt_shutdown','r1_sdk_power_shutdown_process','nrf_atomic_u32_fetch_store','r1_power_log_marker','r1_power_system_reset','POWER_CLOCK_IRQHandler','r1_power_clock_irq0_vector','nrfx_clock_init','nrfx_clock_enable','nrfx_clock_lfclk_start','nrfx_clock_lfclk_stop','r1_soc_observer_907fc','r1_sdh_state_observer_890f0','r1_sdk_clock_notify','r1_sdk_clock_irq_handler','r1_sdk_clock_item_enqueue','nrf_drv_clock_init','nrf_drv_clock_lfclk_request','nrf_drv_clock_lfclk_release','r1_clock_log_info','r1_sdk_soc_events_poll','r1_soc_observer_priority0','r1_soc_observer_priority1','nrf_sdh_is_enabled','nrf_sdh_evts_poll','nrf_sdh_request_continue','nrf_sdh_enable_request','nrf_sdh_disable_request','r1_sdh_stack_observers','r1_sdh_native_state_observers','strncmp','r1_kv_flash_erase_scan','r1_latest_valid_flash_slot_scan_adapter'):assert name in syms
        assert syms['r1_native_bae8_context_get']==syms['blcm_link_ctx_get']
        assert syms['r1_sdk_ble_stack_enabled']==0x20007a1b and syms['r1_sdk_ble_observer_sections']==0x9ca70 and syms['r1_sdk_ble_observer_set']==0x9ca94
        for i,letter in enumerate('abc'):assert syms['r1_ble_qwr_context_'+letter]==0x20007e40+i*12
        assert syms['r1_ble_advertising_context_a']==0x20007e64 and syms['r1_ble_advertising_context_b']==0x200082b0
        assert syms['r1_advertising_product_payload']==0x20007e04 and syms['r1_advertising_connection_intervals']==0x99114
        assert syms['r1_kv_port']==0x20006974 and syms['r1_kv_mutex']==0x20006978 and syms['r1_kv_block_cursor']==0x20019e49 and syms['r1_kv_native_port_record']==0x20006984
        assert syms['r1_ble_gatt_context']==0x20007e1c
        assert syms['r1_sdk_connection_observer']==0xc4568
        assert syms['m_bcs']==0x2002bdb0
        assert syms['r1_ble_link_semaphores']==0x200064fc
        assert syms['nrf_nvic_state']==0x2002c2fc
        assert (syms['m_state'],syms['m_alloc_index'],syms['m_wdt_event_handler'])==(0x20007948,0x20007949,0x2000794c)
        mode=UC_MODE_THUMB|(UC_MODE_MCLASS if '--notification-graph' in sys.argv or '--synchronization' in sys.argv or '--message-queue' in sys.argv or '--logger-pipeline' in sys.argv or '--rtc-startup' in sys.argv or '--initcall-stage' in sys.argv or '--initcall-real-heap' in sys.argv or '--initcall-real-scheduler' in sys.argv or '--queue-lifecycle' in sys.argv or '--queue-timeout' in sys.argv or '--task-construction' in sys.argv or '--thread-construction' in sys.argv or '--application-threads' in sys.argv or '--task-termination' in sys.argv or '--idle-loop' in sys.argv or '--idle-real-sleep' in sys.argv or '--scheduler-start' in sys.argv or '--port-start' in sys.argv or '--context-start' in sys.argv or '--stack-overflow' in sys.argv else 0);stock=Uc(UC_ARCH_ARM,mode);candidate=Uc(UC_ARCH_ARM,mode);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x40000);uc.mem_map(0x1100000,0x1000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        for address,size in tick_variables.values():assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
        assert syms['prvSampleTimeNow.xLastTime']==0x20007864 and bytes(stock.mem_read(0x20007864,4))==bytes(candidate.mem_read(0x20007864,4))==bytes(4)
        for address in (0x20007e64,0x200082b0):assert bytes(stock.mem_read(address,1076))==bytes(candidate.mem_read(address,1076))==bytes(1076)
        for address,size in ((0x20006974,4),(0x20006978,4),(0x20019e49,1)):assert bytes(stock.mem_read(address,size))==bytes(candidate.mem_read(address,size))==bytes(size)
        assert bytes(stock.mem_read(0x20007e04,21))==bytes(candidate.mem_read(0x20007e04,21))==bytes(21)
        assert bytes(stock.mem_read(0x20007e1c,36))==bytes(candidate.mem_read(0x20007e1c,36))==bytes(36)
        assert bytes(stock.mem_read(0x20007e40,36))==bytes(candidate.mem_read(0x20007e40,36))==bytes(36)
        assert bytes(stock.mem_read(0x20007a1b,1))==bytes(candidate.mem_read(0x20007a1b,1))==bytes(1)
        assert bytes(stock.mem_read(0x2002bdb0,124))==bytes(candidate.mem_read(0x2002bdb0,124))==bytes(124)
        assert bytes(stock.mem_read(0x200064fc,8))==bytes(candidate.mem_read(0x200064fc,8))==bytes(8)
        assert bytes(stock.mem_read(0x2002c2fc,12))==bytes(candidate.mem_read(0x2002c2fc,12))==bytes(12)
        candidate.mem_map(0x27000,0x1000);candidate.mem_map(0x30000,0x10000);candidate.mem_map(0x90000,0x10000);candidate.mem_map(0x60000,0x10000);candidate.mem_map(0x70000,0x10000);candidate.mem_map(0x40000,0x10000);candidate.mem_map(0x50000,0x10000);candidate.mem_map(0xb0000,0x10000);candidate.mem_map(0xc0000,0x10000);source_text_bytes=len(text.read_bytes());assert source_text_bytes<0x40000;candidate.mem_write(0x1000000,text.read_bytes())
        for section,address in [('.r1.stack_overflow.ring',0x95c44),('.r1.stack_overflow.nordic',0x95c70)]:
            overflow_file=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(overflow_file),str(elf)],check=True);payload=overflow_file.read_bytes();assert bytes(stock.mem_read(address,len(payload)))==payload;candidate.mem_write(address,payload)
        for section,address,native,symbol in [('.r1.application.initial_sp',0x27000,0x2003beb8,None),('.r1.application.svc_vector',0x2702c,0x27219,'SVC_Handler'),('.r1.application.pendsv_vector',0x27038,0x2725d,'PendSV_Handler')]:
            vector_file=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(vector_file),str(elf)],check=True);payload=vector_file.read_bytes();assert len(payload)==4 and struct.unpack('<I',payload)[0]==(native if symbol is None else syms[symbol]|1) and struct.unpack('<I',bytes(stock.mem_read(address,4)))[0]==native;candidate.mem_write(address,payload)
        fal_partition_record_bytes=0
        kv_scan_descriptor_bytes=0
        kv_init_descriptor_bytes=0
        kv_put_descriptor_bytes=0
        kv_get_descriptor_bytes=0
        bae8_descriptor_bytes=0;gatt_descriptor_bytes=0;advertising_descriptor_bytes=0
        for index,(section,address) in enumerate(tuple(LOGGER_SECTIONS.items())+(('.r1.stacmd_retry.ring',0x3570c),('.r1.stacmd_retry.sdk',0x3573c))+tuple(('.r1.thread_init_log.'+n,a) for n,a in THREAD_LOG_DESCRIPTORS.items())+(('.rodata.r1_fal_partition_records',0x9c250),)+tuple(('.r1.kv.scan.log.'+n,a) for n,a in KV_SCAN_STRINGS.items())+(('.r1.kv.mutex_attributes',0x9a0e8),)+tuple(('.r1.kv.init.log.'+n,a) for n,a in KV_INIT_STRINGS.items())+tuple(('.r1.kv.put.log.'+n,a) for n,a in KV_PUT_STRINGS.items())+tuple(('.r1.kv.get.log.'+n,a) for n,a in KV_GET_STRINGS.items())+(('.r1.advertising.intervals',0x99114),)+tuple(('.r1.advertising.log.'+n,a) for n,a in ADVERTISING_DESCRIPTORS.items())+tuple(('.r1.gatt.log.'+n,a) for n,a in GATT_DESCRIPTORS.items())+tuple(observer_data_sections)+(('.sdh_ble_observers0',0xc4568),)+tuple(('.r1.bae8.log.'+n,a) for n,a in DESCRIPTORS.items())+(( '.r1.output.ring',0x44fec),('.r1.output.sdk',0x4501c),( '.wdt.log.init',0x7b5f8),('.wdt.log.alloc',0x7b4e4),('.wdt.log.enable',0x7b560),('.r1.watchdog.port',0x993d0),('.r1.watchdog.mutex_attributes',0x993c0),('.r1.wdt.state',0x20007630),('.r1.connection.field8',0x200064ba),('.r1.connection.field10',0x200064bc),('.r1.tx.channel1',0x200065bc),('.r1.tx.shared',0x200065e0),('.r1.connection.field6',0x200064b8),('.r1.event.sensor',0x2000668c),('.r1.event.system',0x20006608),('.r1.event.storage',0x200066d8),('.r1.log.cache',0x200068f4),('.r1.log.level',0x200068ed),('.r1.log.mode',0x200068ec),('.r1.i2c5.state',0x20006838),('.r1.adc.state',0x20006ef4),('.r1.adc.ops',0x20006f70),('.r1.gpio.records',0x200070c0),('.r1.gpio.ops',0x200071f4),('.r1.twi.records',0x20007400))):
            path=tmp/(str(index)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);candidate.mem_write(address,path.read_bytes())
            if section.startswith(('.r1.thread_init_log.','.r1.stacmd_retry.')):assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section in LOGGER_SECTIONS:assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section=='.rodata.r1_fal_partition_records':fal_partition_record_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.kv.scan.log.'):kv_scan_descriptor_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.kv.init.log.') or section=='.r1.kv.mutex_attributes':kv_init_descriptor_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.kv.put.log.'):kv_put_descriptor_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.kv.get.log.'):kv_get_descriptor_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.advertising.'):advertising_descriptor_bytes+=len(path.read_bytes());assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
            if section.startswith('.r1.gatt.log.'):gatt_descriptor_bytes+=len(path.read_bytes())
            if section.startswith('.r1.bae8.log.'):bae8_descriptor_bytes+=len(path.read_bytes())
            if section.startswith(('.r1.gatt.log.','.wdt.log.','.r1.output.','.r1.bae8.log.')):assert bytes(stock.mem_read(address,len(path.read_bytes())))==path.read_bytes()
        for n,(a,z) in KV_INIT_FIELDS.items():assert bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        from verify_native_device_registrars import GPIO_POINTERS,STACMD_POINTERS,NAMES
        for section,address,z,pointers in [('.r1.stacmd.failed_transactions',0x200075c0,4,[]),('.r1.output_gpio.configuration',0x20007228,340,GPIO_POINTERS),('.r1.stacmd.configuration',0x200075c4,108,STACMD_POINTERS),*[(('.r1.output_gpio.name'+str(i)) if i<5 else '.r1.stacmd.name',a,len(n)+1,[]) for i,(a,n) in enumerate(NAMES)]]:
            path=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);data=path.read_bytes();assert len(data)==z;normalized=bytearray(data)
            for off,name,native in pointers:assert struct.unpack_from('<I',data,off)[0]==syms[name]|1;struct.pack_into('<I',normalized,off,native|1)
            assert bytes(normalized)==bytes(stock.mem_read(address,z));candidate.mem_write(address,data)
        from verify_native_hw_twi_registration import POINTERS as HW_TWI_POINTERS
        for section,address,z in [('.r1.hw_twi.primary',0x20006fe8,108),('.r1.hw_twi.secondary',0x20007054,108),('.r1.hw_twi.name0',0xc06e4,6),('.r1.hw_twi.name1',0xc06ec,6)]:
            path=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);data=path.read_bytes();assert len(data)==z;normalized=bytearray(data)
            for offset,name,native in HW_TWI_POINTERS:
                relative=0x20006fe8+offset-address
                if 0<=relative<=z-4:assert struct.unpack_from('<I',data,relative)[0]==syms[name]|1;struct.pack_into('<I',normalized,relative,native|1)
            assert bytes(normalized)==bytes(stock.mem_read(address,z));candidate.mem_write(address,data)
        init_table_path=tmp/'device-initcalls.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.init.devices='+str(init_table_path),str(elf)],check=True);init_table=init_table_path.read_bytes();assert len(init_table)==52
        from verify_native_initcalls import CALLS as INITCALLS
        for i,(name,address) in enumerate(INITCALLS):assert struct.unpack_from('<I',init_table,i*4)[0]==syms[name]|1 and struct.unpack('<I',bytes(stock.mem_read(0xc4534+i*4,4)))[0]==address|1
        candidate.mem_write(0xc4534,init_table)
        rtc_vector_path=tmp/'rtc-irq36-vector.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.rtc.irq36.vector='+str(rtc_vector_path),str(elf)],check=True);rtc_vector=rtc_vector_path.read_bytes();assert len(rtc_vector)==4 and struct.unpack('<I',rtc_vector)[0]==syms['RTC2_IRQHandler']|1 and struct.unpack('<I',bytes(stock.mem_read(0x270d0,4)))[0]==0x31751;candidate.mem_write(0x270d0,rtc_vector)
        assert syms['r1_rtc_driver_error']==syms['r1_adc_error']
        assert syms['r1_sdk_rtc_control']==0x20007950 and syms['r1_sdk_rtc_handlers']==0x20007954 and bytes(stock.mem_read(0x20007950,8))==bytes(candidate.mem_read(0x20007950,8))==bytes(8)
        assert syms['r1_rtc_device_ops']==0x200073dc and syms['r1_rtc_boot_defaults']==0x9a638
        assert bytes(stock.mem_read(0x20037e88,32))==bytes(candidate.mem_read(0x20037e88,32))==bytes(32)
        for section,address,z in [('.r1.rtc.log.enabled',0x7ad5c,15),('.r1.rtc.log.tick',0x7ae90,27),('.r1.rtc.log.function',0x7ae28,36),('.r1.rtc.defaults',0x9a638,8),('.r1.rtc.months',0xbdb18,12),('.r1.rtc.ops',0x200073dc,36)]:
            path=tmp/(str(address)+'-rtc-life.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==z
            if section!='.r1.rtc.ops':assert payload==bytes(stock.mem_read(address,z))
            else:
                for i,native,name in [(2,0x56318,'r1_native_rtc_open'),(4,0x5639c,'r1_native_rtc_snapshot'),(5,0x5649c,'r1_native_rtc_epoch_initialize'),(7,0x563f8,'r1_native_rtc_calendar_write'),(8,0x56444,'r1_native_rtc_callback_bind')]:assert struct.unpack_from('<I',payload,i*4)[0]==syms[name]|1 and struct.unpack('<I',bytes(stock.mem_read(address+i*4,4)))[0]==native|1
                for i in (0,1,3,6):assert struct.unpack_from('<I',payload,i*4)[0]==0 and bytes(stock.mem_read(address+i*4,4))==bytes(4)
            candidate.mem_write(address,payload)
        assert syms['r1_rtc_counter']==0x2000737c and syms['r1_rtc_record']==0x20007384 and syms['r1_rtc_device_name']==0xc07a0
        assert bytes(stock.mem_read(0x2000737c,8))==bytes(candidate.mem_read(0x2000737c,8))==bytes(8)
        for section,address,z in [('.r1.rtc.record',0x20007384,88),('.r1.rtc.name',0xc07a0,8)]:
            path=tmp/(str(address)+'-rtc.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==z and payload==bytes(stock.mem_read(address,z));candidate.mem_write(address,payload)
        assert syms['r1_clock_default_backend']==0x99c8c and syms['r1_clock_boot_defaults']==0x99c54
        for section,address,z in [('.r1.clock.backend',0x99c8c,32),('.r1.clock.defaults',0x99c54,8)]:
            path=tmp/(str(address)+'-clock-boot.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==z
            if z==8:assert payload==bytes(stock.mem_read(address,z))
            else:
                native=(0x50d86,0x50d60,0x50d7e,0x50d82,0x50db6,0x50d64,0x50d8a,0x50daa);names=('default_init','default_deinit','default_get','r1_clock_backend_slot12','r1_clock_backend_update','r1_clock_backend_slot20','r1_clock_backend_slot24','r1_clock_backend_bind_tick')
                for i,(v,n) in enumerate(zip(native,names)):assert struct.unpack_from('<I',payload,i*4)[0]==syms[n]|1 and struct.unpack('<I',bytes(stock.mem_read(address+i*4,4)))[0]==v|1
            candidate.mem_write(address,payload)
        assert syms['r1_log_module_records']==syms['__start_log_const_data']==0xc441c and syms['__stop_log_const_data']==0xc451c
        for section,address,z in [('.r1.log.modules',0xc441c,256)]+[('.r1.log.module_name.'+str(row['index']),int(row['name_address'],16),len(row['name'])+1) for row in module_config['rows']]:
            path=tmp/(str(address)+'-module.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==z and payload==bytes(stock.mem_read(address,z));candidate.mem_write(address,payload)
        colors=tmp/'formatter-colors.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.data.m_colors='+str(colors),str(elf)],check=True);payload=colors.read_bytes();assert len(payload)==36;candidate.mem_write(0x200079f4,payload)
        def log_color_string(uc,address):
            data=bytearray()
            for i in range(16):
                byte=uc.mem_read(address+i,1)[0]
                if not byte:return bytes(data)
                data.append(byte)
            raise AssertionError('unterminated color')
        for i in range(9):assert log_color_string(stock,struct.unpack('<I',bytes(stock.mem_read(0x200079f4+i*4,4)))[0])==log_color_string(candidate,struct.unpack_from('<I',payload,i*4)[0])
        for n,(a,z) in SEGGER_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        for section,address,z in [('.r1.rtt.terminal',0x36dbc,9),('.r1.rtt.identifier',0x9ca04,16)]:
            path=tmp/(str(address)+'-segger.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==z and payload==bytes(stock.mem_read(address,z));candidate.mem_write(address,payload)
        for n,(a,z) in RTT_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        for section,address in RTT_SECTIONS.items():
            path=tmp/(str(address)+'-rtt.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();native=bytes(stock.mem_read(address,len(payload)))
            if section=='.rodata.nrf_log_backend_rtt_api':
                for i,name in enumerate(('nrf_log_backend_rtt_put','nrf_log_backend_rtt_panic_set','nrf_log_backend_rtt_flush')):assert struct.unpack_from('<I',payload,i*4)[0]==syms[name]|1 and struct.unpack_from('<I',native,i*4)[0]==RTT_ENTRIES[name]|1
            else:assert payload==native,(section,payload,native)
            candidate.mem_write(address,payload)
        for n,(a,z) in LOGGER_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        for n,(a,z) in POWER_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        vector_path=tmp/'clock-irq0-vector.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.clock.irq0.vector='+str(vector_path),str(elf)],check=True);vector=vector_path.read_bytes();assert len(vector)==4 and struct.unpack('<I',vector)[0]==syms['POWER_CLOCK_IRQHandler']|1 and struct.unpack('<I',bytes(stock.mem_read(0x27040,4)))[0]==0x30ac9;candidate.mem_write(0x27040,vector)
        assert syms['r1_sdk_nrfx_clock_control']==0x20007938 and bytes(stock.mem_read(0x20007938,8))==bytes(candidate.mem_read(0x20007938,8))==bytes(8)
        assert syms['r1_sdk_clock_control']==0x2002c154 and bytes(stock.mem_read(0x2002c154,20))==bytes(candidate.mem_read(0x2002c154,20))==bytes(20)
        for section,address in soc_sections.items():
            path=tmp/('soc-'+str(address)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();candidate.mem_write(address,payload)
            if section.startswith('.rodata.'):assert payload==bytes(stock.mem_read(address,len(payload)))
            else:
                name='r1_soc_observer_907fc' if section=='.r1.soc.observer0' else 'ble_dfu_buttonless_on_sys_evt';native=0x907fd if section=='.r1.soc.observer0' else 0x52279
                assert len(payload)==8 and struct.unpack('<2I',payload)==(syms[name]|1,0) and struct.unpack('<2I',bytes(stock.mem_read(address,8)))==(native,0)
        for i,n in enumerate(('m_nrf_sdh_enabled','m_nrf_sdh_suspended','m_nrf_sdh_continue')):assert syms[n]==0x20007a18+i and bytes(stock.mem_read(0x20007a18+i,1))==bytes(candidate.mem_read(0x20007a18+i,1))==bytes(1)
        for section,address in sdh_sections.items():
            path=tmp/('sdh-'+str(address)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();candidate.mem_write(address,payload)
            if section.startswith('.rodata.'):assert payload==bytes(stock.mem_read(address,len(payload)))
            else:
                names=('r1_sdk_ble_events_poll','r1_sdk_soc_events_poll') if section=='.r1.sdh.stack.records' else ('r1_sdh_state_observer_567ac','r1_sdh_state_observer_890f0')
                native=(0x7a38d,0x7a501) if section=='.r1.sdh.stack.records' else (0x567ad,0x890f1)
                assert len(payload)==16 and struct.unpack('<4I',payload)==(syms[names[0]]|1,0,syms[names[1]]|1,0)
                assert struct.unpack('<4I',bytes(stock.mem_read(address,16)))==(native[0],0,native[1],0)
        for n,(a,z) in SD_FSTORAGE_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        for section,address in (('.r1.fstorage_sd.fifo_pointer',0x9c85c),('.rodata.r1_sdk_fstorage_sd_flash_info',0x9c860),('.rodata.nrf_fstorage_sd',0x9c86c))+tuple(('.sdh_'+n+'_observers0',a) for n,(a,h) in SD_FSTORAGE_OBSERVERS.items()):
            path=tmp/('sd-fstorage-'+str(address)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);payload=path.read_bytes();candidate.mem_write(address,payload)
            if address==0x9c85c:assert payload==bytes(stock.mem_read(address,4))==struct.pack('<I',0x2002c3f8)
            elif address==0x9c860:assert len(payload)==12 and payload==bytes(stock.mem_read(address,12))
            elif address==0x9c86c:
                assert len(payload)==32 and struct.unpack('<8I',payload)==tuple(syms['r1_sdk_fstorage_sd_'+n]|1 for n in SD_FSTORAGE_API)
                assert struct.unpack('<8I',bytes(stock.mem_read(address,32)))==tuple(a|1 for a in SD_FSTORAGE_API.values())
            else:
                name,handler=next((n,h) for n,(a,h) in SD_FSTORAGE_OBSERVERS.items() if a==address)
                from verify_sdk_fstorage_sd import EXTRA as SD_FSTORAGE_EXTRA
                assert struct.unpack('<2I',payload)==(syms[handler]|1,0) and struct.unpack('<2I',bytes(stock.mem_read(address,8)))==(SD_FSTORAGE_EXTRA[handler]|1,0)
        from verify_native_internal_flash import ENTRIES as INTERNAL_FLASH_ENTRIES
        assert syms['__start_fs_data']==0x20007dc0 and syms['__stop_fs_data']==0x20007de8
        assert syms['r1_internal_flash_pending']==0x20006f96 and bytes(stock.mem_read(0x20006f96,1))==bytes(candidate.mem_read(0x20006f96,1))==b'\0'
        internal_flash_sections_data={}
        for suffix,address,size in (('name',0xc06d4,13),('record',0x20006f98,80),('fstorage',0x20007dc0,20)):
            path=tmp/('internal-flash-'+suffix+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.flash.'+suffix+'='+str(path),str(elf)],check=True);payload=path.read_bytes();assert len(payload)==size;candidate.mem_write(address,payload);internal_flash_sections_data[suffix]=payload
        assert bytes(stock.mem_read(0xc06d4,13))==internal_flash_sections_data['name'] and bytes(stock.mem_read(0x20006f98,44))==internal_flash_sections_data['record'][:44]
        flash_ops={44:'r1_internal_flash_fstorage_configuration',60:'r1_internal_flash_device_read',64:'r1_internal_flash_device_write',68:'r1_internal_flash_erase_and_geometry_control',72:'r1_internal_flash_callback_configuration'}
        for offset in range(44,80,4):
            assert struct.unpack_from('<I',internal_flash_sections_data['record'],offset)[0]==(syms[flash_ops[offset]]|1 if offset in flash_ops else 0)
            assert struct.unpack('<I',bytes(stock.mem_read(0x20006f98+offset,4)))[0]==(INTERNAL_FLASH_ENTRIES[flash_ops[offset]]|1 if offset in flash_ops else 0)
        assert internal_flash_sections_data['fstorage'][:8]==bytes(stock.mem_read(0x20007dc0,8)) and internal_flash_sections_data['fstorage'][12:]==bytes(stock.mem_read(0x20007dcc,8))
        assert struct.unpack_from('<I',internal_flash_sections_data['fstorage'],8)[0]==(syms['r1_internal_flash_event_handler']|1) and struct.unpack('<I',bytes(stock.mem_read(0x20007dc8,4)))[0]==0x65721
        for n,(a,z) in NATIVE_FAL_FIELDS.items():assert syms['r1_fal_'+n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        native_fal_record=tmp/'native-fal-record.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.fal.device_record='+str(native_fal_record),str(elf)],check=True);candidate.mem_write(0x200077c4,native_fal_record.read_bytes());assert len(native_fal_record.read_bytes())==56
        assert bytes(stock.mem_read(0x200077c4,36))==native_fal_record.read_bytes()[:36] and bytes(stock.mem_read(0x200077f8,4))==native_fal_record.read_bytes()[52:]
        assert struct.unpack_from('<4I',native_fal_record.read_bytes(),36)==tuple(syms[n]|1 for n in NATIVE_FAL_ENTRIES)
        assert struct.unpack('<4I',bytes(stock.mem_read(0x200077e8,16)))==tuple(a|1 for a in NATIVE_FAL_ENTRIES.values())
        for n,(a,z) in FAL_PARTITION_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        assert syms['r1_fal_device_initialized']==0x200077b2 and bytes(stock.mem_read(0x200077b2,1))==bytes(candidate.mem_read(0x200077b2,1))==b'\0'
        assert syms['r1_fal_initialized']==0x200077b1 and syms['r1_fal_is_initialized']==syms['fal_init_check']
        assert bytes(stock.mem_read(0x200077b1,1))==bytes(candidate.mem_read(0x200077b1,1))==b'\0'
        from verify_native_kv_port import TABLE as KV_PORT_TABLE
        kv_data=tmp/'kv-port.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.kv.port_record='+str(kv_data),str(elf)],check=True);candidate.mem_write(0x20006984,kv_data.read_bytes());assert len(kv_data.read_bytes())==36
        assert struct.unpack('<9I',bytes(stock.mem_read(0x20006984,36)))==tuple(address|1 for name,address in KV_PORT_TABLE)
        assert struct.unpack('<9I',bytes(candidate.mem_read(0x20006984,36)))==tuple(syms[name]|1 for name,address in KV_PORT_TABLE)
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
        assert syms['xTaskCreate']==syms['r1_native_task_create'] and syms['xTaskCreateStatic']==syms['r1_native_task_create_static'] and syms['r1_native_initial_xpsr']==0x9c4cc
        xpsr_data=tmp/'task-initial-xpsr.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.task.initial_xpsr='+str(xpsr_data),str(elf)],check=True);assert xpsr_data.read_bytes()==bytes(stock.mem_read(0x9c4cc,4))==struct.pack('<I',0x1000000);candidate.mem_write(0x9c4cc,xpsr_data.read_bytes())
        assert syms['uxTopUsedPriority']==0x2000784c
        priority_data=tmp/'top-used-priority.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.scheduler.top_used_priority='+str(priority_data),str(elf)],check=True);assert priority_data.read_bytes()==bytes(stock.mem_read(0x2000784c,4))==struct.pack('<I',55);candidate.mem_write(0x2000784c,priority_data.read_bytes())
        for n,(a,z) in SCHEDULER_FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        assert (syms['r1_heap_storage'],syms['r1_heap_start'],syms['r1_heap_state'])==(0x2001e588,0x2002ad88,0x200077fc)
        for a,z in ((0x200077fc,20),(0x2001e588,51200),(0x2002ad88,12)):assert bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
        from unicorn import UC_HOOK_CODE
        fixture_allow=set()
        def trap(uc,address,size,data):
            if 0x1100000<=address<0x1101000 and address not in fixture_allow:raise AssertionError('Unresolved production seam invoked')
        candidate.hook_add(UC_HOOK_CODE,trap)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
        baseline={id(uc):bytes(uc.mem_read(0x20000000,0x40000)) for uc in (stock,candidate)}
        if '--logger-pipeline' in sys.argv:
            from verify_logger_pipeline import verify
            verify(stock,candidate,syms,baseline)
        if '--thread-init-logs-graph' in sys.argv:
            from verify_thread_init_logs_graph import verify as verify_init_logs
            verify_init_logs(stock,candidate,syms,baseline)
        if '--rtc-startup' in sys.argv:
            from verify_rtc_startup import verify as verify_rtc
            verify_rtc(stock,candidate,syms,baseline)
        if '--initcall-stage' in sys.argv:
            from verify_initcall_stage import verify as verify_stage
            verify_stage(stock,candidate,syms,baseline,fixture_allow)
        if '--initcall-real-heap' in sys.argv:
            from verify_initcall_stage import verify as verify_heap_stage
            verify_heap_stage(stock,candidate,syms,baseline,fixture_allow,real_heap=True)
        if '--initcall-real-scheduler' in sys.argv:
            from verify_initcall_stage import verify as verify_scheduler_stage
            verify_scheduler_stage(stock,candidate,syms,baseline,fixture_allow,real_heap=True,real_scheduler=True)
        if '--notification-graph' in sys.argv:
            from verify_notification_graph import verify as verify_notifications
            verify_notifications(stock,candidate,syms,baseline)
        if '--synchronization' in sys.argv:
            from verify_synchronization_graph import verify as verify_synchronization
            verify_synchronization(stock,candidate,syms,baseline)
        if '--message-queue' in sys.argv:
            from verify_message_queue_graph import verify as verify_message_queues
            verify_message_queues(stock,candidate,syms,baseline)
        if '--queue-lifecycle' in sys.argv:
            from verify_queue_lifecycle import verify as verify_lifecycle
            verify_lifecycle(stock,candidate,syms,baseline)
        if '--queue-timeout' in sys.argv:
            from verify_queue_timeout import verify as verify_timeout
            verify_timeout(stock,candidate,syms,baseline)
        if '--task-construction' in sys.argv:
            from verify_task_construction_graph import verify as verify_construction
            verify_construction(stock,candidate,syms,baseline)
        if '--thread-construction' in sys.argv:
            from verify_task_construction_graph import verify as verify_thread_construction
            verify_thread_construction(stock,candidate,syms,baseline,cmsis=True)
        if '--stack-overflow' in sys.argv:
            from verify_stack_overflow_graph import verify as verify_stack_overflow
            verify_stack_overflow(stock,candidate,syms,baseline)
        if '--context-start' in sys.argv:
            from verify_context_start_graph import verify as verify_context_start
            verify_context_start(stock,candidate,syms,baseline,fixture_allow)
        if '--port-start' in sys.argv:
            from verify_scheduler_start_graph import verify as verify_port_start
            verify_port_start(stock,candidate,syms,baseline,fixture_allow,real_port=True)
        if '--scheduler-start' in sys.argv:
            from verify_scheduler_start_graph import verify as verify_scheduler_start
            verify_scheduler_start(stock,candidate,syms,baseline,fixture_allow)
        if '--idle-real-sleep' in sys.argv:
            from verify_idle_loop_graph import verify as verify_idle_real_sleep
            verify_idle_real_sleep(stock,candidate,syms,baseline,fixture_allow,real_sleep=True)
        if '--idle-loop' in sys.argv:
            from verify_idle_loop_graph import verify as verify_idle_loop
            verify_idle_loop(stock,candidate,syms,baseline,fixture_allow)
        if '--task-termination' in sys.argv:
            from verify_task_termination_graph import verify as verify_task_termination
            verify_task_termination(stock,candidate,syms,baseline)
        if '--application-threads' in sys.argv:
            from verify_application_thread_creation import verify as verify_app_threads
            verify_app_threads(stock,candidate,syms,baseline)
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
    result=dict(application_sha256=sha(app),board_report_sha256=sha(BASE/'board/report.json'),relocatable_sha256=sha(obj),binary_runtime_linked=False,cache_initialization_bytes_compared=8444,event_context_prefix_initial_bytes_compared=48,tx_context_prefix_initial_bytes_compared=32,task_zero_initial_bytes_compared=28208,connection_initial_bytes_compared=6,sync_watchdog_initial_bytes_compared=24,watchdog_registry_current_task_initial_bytes_compared=25,watchdog_startup_initial_zero_bytes_compared=88,wdt_sdk_initial_control_bytes_compared=8,nvic_initial_zero_bytes_compared=12,watchdog_log_descriptor_bytes_compared=87,output_descriptor_bytes_compared=68,ble_semaphore_initial_zero_bytes_compared=8,connection_state_candidate_initial_zero_bytes_compared=124,registry_observer_record_bytes_pointer_normalized=8,ble_observer_table_bytes_pointer_normalized=96,ble_observer_range_set_bytes_compared=44,gatt_log_descriptor_bytes_compared=gatt_descriptor_bytes,kv_scan_descriptor_bytes_compared=kv_scan_descriptor_bytes,logger_frontend_initial_zero_bytes_compared=4128,rtc_cold_bytes_compared=104,clock_default_backend_bytes_pointer_normalized=32,clock_default_config_bytes_compared=8,log_module_record_bytes_compared=256,log_module_name_bytes_compared=311,formatter_colors_bytes_pointer_normalized=36,segger_initial_zero_bytes_compared=696,segger_terminal_name_bytes_compared=9,segger_reverse_identifier_bytes_compared=16,rtt_initial_zero_bytes_compared=4097,rtt_backend_control_bytes_compared=8,rtt_backend_record_bytes_compared=16,rtt_backend_api_bytes_pointer_normalized=12,rtt_backend_name_bytes_compared=16,logger_push_ring_initial_zero_bytes_compared=152,logger_push_ring_descriptor_bytes_compared=12,logger_pool_initial_zero_bytes_compared=208,logger_mask_bytes_compared=4,logger_pool_descriptor_bytes_compared=20,logger_warning_bytes_compared=40,power_initial_zero_bytes_compared=sum(z for a,z in POWER_FIELDS.values()),clock_irq0_vector_bytes_pointer_normalized=4,nrfx_clock_initial_zero_bytes_compared=8,clock_initial_zero_bytes_compared=20,soc_range_set_bytes_compared=28,soc_observer_bytes_pointer_normalized=16,sdh_state_initial_zero_bytes_compared=3,sdh_range_set_bytes_compared=84,sdh_observer_bytes_pointer_normalized=32,sd_fstorage_initial_zero_bytes_compared=sum(z for a,z in SD_FSTORAGE_FIELDS.values()),sd_fstorage_api_bytes_pointer_normalized=32,sd_fstorage_fifo_pointer_bytes_compared=4,sd_fstorage_flash_info_bytes_compared=12,sd_fstorage_observer_bytes_pointer_normalized=24,internal_flash_pending_initial_zero_bytes_compared=1,internal_flash_record_bytes_pointer_normalized=80,internal_flash_fstorage_bytes_pointer_normalized=20,internal_flash_name_bytes_compared=13,native_fal_record_bytes_pointer_normalized=56,native_fal_initial_zero_bytes_compared=sum(z for a,z in NATIVE_FAL_FIELDS.values()),fal_partition_record_bytes_compared=fal_partition_record_bytes,fal_partition_initial_zero_bytes_compared=sum(z for a,z in FAL_PARTITION_FIELDS.values()),fal_device_initial_zero_bytes_compared=1,fal_readiness_initial_zero_bytes_compared=1,kv_init_initial_zero_bytes_compared=sum(z for a,z in KV_INIT_FIELDS.values()),kv_init_descriptor_bytes_compared=kv_init_descriptor_bytes,kv_put_descriptor_bytes_compared=kv_put_descriptor_bytes,kv_get_descriptor_bytes_compared=kv_get_descriptor_bytes,kv_port_record_bytes_pointer_normalized=36,kv_port_initial_zero_bytes_compared=9,advertising_product_descriptor_bytes_compared=advertising_descriptor_bytes,advertising_product_payload_zero_bytes_compared=21,advertising_compatible_context_zero_bytes_compared=2152,gatt_context_initial_zero_bytes_compared=36,qwr_context_initial_zero_bytes_compared=36,ble_stack_initial_zero_bytes_compared=1,bae8_descriptor_bytes_compared=bae8_descriptor_bytes,unresolved_test_guard_base='0x1100000',source_text_bytes=source_text_bytes,rtos_tick_critical_initial_zero_bytes_compared=21,timer_sample_state_initial_zero_bytes_compared=4,watchdog_device_state_bytes_compared=80,watchdog_port_table_bytes_compared=12,comparisons=comparisons,registry_records=15,registration_group_orders=24,resolved_handles={'nfc_gpo_irq':'0x200071ac','i2c_5':'0x20007584','vnfc_rect_adc':'0x20006f58'},scope='Actual source-owned WDT/ADC/GPIO/TWI records populate one registry; original versus compiled registration/discovery match across all group orders without prebound handles',test_only_bindings=['Unresolved function providers are test-only traps; dispatch tables, BAE8 service and opaque observer contexts are address-only bindings without initial content/extent proof'],limitations=['Physical logging transport, actual clock registration and complete application startup remain unproven.','All memory/string code in this executable comes from compiled, attributable C providers; original Arm runtime identity remains unproven.','This does not establish complete application startup, hardware behavior or instruction identity.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{comparisons} native board comparisons passed across 24 registration orders; all three NFC handles resolve from 15 real records')
if __name__=='__main__':main()
