#!/usr/bin/env python3
"""Account for every ownership entry without upgrading symbol hints to closure."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'r1/research/source-build'
REPORTS=['sdk-advertising-init/report.json','sdk-advertising/report.json','native-gatt/report.json','sdk-gatt/report.json','sdk-qwr/report.json','sdk-ble-dispatch/report.json','sdk-connection-events/report.json','sdk-connection-index/report.json','sdk-link-context/report.json','native-bae8-send/report.json','native-ble-send/report.json','native-output/report.json','watchdog-logging/report.json','sdk-critical/report.json','integer-runtime/report.json','report.json','bootloader/report.json','public-providers/report.json','rtos/report.json','crypto/report.json','application-sdk/report.json','goodix/report.json','sensors/report.json','i2c5/report.json','software-twi/gpio-report.json','gpio/report.json','adc/report.json','runtime/report.json','board-seams/report.json','structured-log/report.json','rtos-critical/report.json','structured-encode/report.json','structured-time/report.json','rtos-ticks/report.json','structured-float/report.json','structured-cache/report.json','structured-cache-copy/report.json','native-events/report.json','connection-handle/report.json','native-tx/report.json','native-task-lifecycle/report.json','native-tasks/report.json','native-sync/report.json','native-watchdog/report.json','native-event-dispatch/report.json','watchdog-startup/report.json']
VERIFIED={
 **{entry:(name,'sdk-advertising-init/verification.json') for entry,name in (('0x00051716','ble_advertising_init'),('0x00051528','ble_advdata_encode'),('0x00051fb8','r1_sdk_adv_device_addr_encode'),('0x00059bde','r1_sdk_adv_conn_int_encode'),('0x00076088','r1_sdk_adv_manuf_encode'),('0x0008aba0','r1_sdk_adv_service_encode'),('0x000770bc','r1_sdk_adv_name_encode'),('0x00095570','r1_sdk_adv_uuid_list_sized_encode'))},
 **{entry:(name,'sdk-advertising/verification.json') for entry,name in (('0x00051806','ble_advertising_on_ble_evt'),('0x00051870','ble_advertising_start'),('0x00051710','ble_advertising_conn_cfg_tag_set'),('0x000517fe','ble_advertising_modes_config_set'),('0x00064f1a','r1_sdk_adv_flags_set'),('0x0007f0c8','r1_sdk_adv_phy_is_valid'),('0x00094dd8','r1_sdk_adv_use_whitelist'),('0x000516aa','ble_advdata_parse'),('0x000516ca','ble_advdata_search'))},
 **{entry:(name,'native-gatt/verification.json') for entry,name in (('0x000781b4','nrf_ble_gatt_on_ble_evt'),('0x0007ce34','r1_gatt_on_mtu_request'),('0x0005a65c','r1_gatt_data_length_update'))},
 **{entry:(name,'sdk-gatt/verification.json') for entry,name in (('0x00078186','nrf_ble_gatt_init'),('0x00074f20','r1_sdk_gatt_link_init'))},
 **{entry:(name,'sdk-qwr/verification.json') for entry,name in (('0x000783b6','nrf_ble_qwr_init'),('0x000783da','nrf_ble_qwr_on_ble_evt'),('0x00095114','r1_sdk_qwr_user_mem_reply'))},
 **{entry:(name,receipt) for entry,name,receipt in (('0x0007a38c','r1_sdk_ble_events_poll','sdk-ble-dispatch/verification.json'),('0x0007a53c','nrf_section_iter_init','sdk-ble-dispatch/iterator-verification.json'),('0x0007a56a','nrf_section_iter_next','sdk-ble-dispatch/iterator-verification.json'))},
 **{entry:(name,'sdk-connection-events/verification.json') for entry,name in (('0x0005380c','r1_sdk_connection_event'),('0x00059ba0','conn_handle_list_get'),('0x00077fbe','nrf_atflags_clear'),('0x00078054','nrf_atflags_set'),('0x00078086','nrf_atomic_u32_and'))},
 **{entry:(name,'sdk-connection-index/verification.json') for entry,name in (('0x00051e04','ble_conn_state_conn_idx'),('0x00051fa4','ble_conn_state_valid'),('0x0007803e','nrf_atflags_get'),('0x00051440','bcs_internal_state_reset'),('0x00051e78','ble_conn_state_init'))},
 '0x000514e0':('blcm_link_ctx_get','sdk-link-context/verification.json'),
 '0x000526cc':('r1_native_bae8_send','native-bae8-send/verification.json'),
 **{entry:(name,'native-ble-send/verification.json') for entry,name in (('0x0003e7a8','r1_native_ble_message_send'),('0x0003e884','r1_ble_error_is_benign'),('0x0003e8ae','r1_ble_flush_one'),('0x0003e8b4','r1_ble_flush_bounded'),('0x0003e8dc','r1_ble_flush_drain'),('0x0003e8fc','r1_ble_link_semaphore'),('0x0003e924','r1_ble_semaphore_take'))},
 **{entry:(name,'native-output/verification.json') for entry,name in (('0x00044f50','r1_native_output_worker'),('0x0004e650','r1_native_ble_send_phone'),('0x0004e65e','r1_native_ble_send_glasses'))},
 '0x0007a594':('nrf_strerror_find','watchdog-logging/strerror-verification.json'),
 '0x0007a5cc':('nrf_strerror_get','watchdog-logging/strerror-verification.json'),
 '0x0004ebec':('app_util_critical_region_enter','sdk-critical/verification.json'),
 '0x0004ec34':('app_util_critical_region_exit','sdk-critical/verification.json'),
 **{address:(name,'integer-runtime/verification.json') for address,name in (('0x000274e8','__aeabi_uldivmod'),('0x0002754a','__aeabi_ldivmod'),('0x000275ac','__aeabi_llsl'),('0x000275ca','__aeabi_llsr'))},
 **{entry:(name,'watchdog-startup/manager-verification.json') for entry,name in [('0x0005da30', 'r1_native_watchdog_expired_task')]},
 **{entry:(name,'watchdog-startup/device-verification.json') for entry,name in [('0x000500c8', 'r1_native_watchdog_hw_close'), ('0x000500d4', 'r1_native_watchdog_hw_handle_init'), ('0x000500fc', 'r1_native_watchdog_hw_feed'), ('0x0005010c', 'r1_native_watchdog_hw_open_feed'), ('0x00095be8', 'r1_native_watchdog_hw_feed_thunk'), ('0x0006623e', 'r1_native_watchdog_port_sample'), ('0x00056638', 'r1_native_named_wdt_feed'), ('0x00056658', 'r1_native_named_wdt_open'), ('0x00056694', 'r1_native_named_wdt_register')]},
 **{entry:(name,'watchdog-logging/verification.json') for entry,name in [('0x00034a7c', 'WDT_IRQHandler'), ('0x0007b470', 'nrfx_wdt_channel_alloc'), ('0x0007b508', 'nrfx_wdt_channel_feed'), ('0x0007b520', 'nrfx_wdt_enable'), ('0x0007b570', 'nrfx_wdt_init')]},

 **{entry:(name,'native-watchdog/verification.json') for entry,name in [('0x0005db14', 'r1_native_watchdog_register'), ('0x0005dbea', 'r1_native_watchdog_arm'), ('0x0005dbbc', 'r1_native_watchdog_disarm'), ('0x0005da00', 'r1_native_watchdog_feed'), ('0x00097730', 'r1_native_watchdog_lock'), ('0x00097748', 'r1_native_watchdog_unlock'), ('0x0005d8e6', 'r1_native_list_head'), ('0x0005d8f6', 'r1_native_list_tail'), ('0x0005d8ee', 'r1_native_list_next'), ('0x00077e30', 'r1_native_list_set_next'), ('0x00077e3c', 'r1_native_list_set_previous'), ('0x0005d8fe', 'r1_native_list_initialize'), ('0x0005d986', 'r1_native_list_empty'), ('0x0005d94a', 'r1_native_list_append'), ('0x0005d90e', 'r1_native_list_prepend'), ('0x0009879c', 'xTaskGetCurrentTaskHandle')]},
 '0x0008d888':('r1_native_event_dispatch','native-event-dispatch/verification.json'),
 **{entry:(name,'native-tasks/verification.json') for entry,name in [('0x000920ec','r1_native_task_gtx'),('0x0009227c','r1_native_task_msgtx'),('0x00092580','r1_native_task_sensor'),('0x000926dc','r1_native_task_service'),('0x00046954','r1_native_task_storage')]},
 **{entry:(name,'native-sync/verification.json') for entry,name in [('0x000923a4','r1_native_suspend_signal'),('0x000923b4','r1_native_sync_wait'),('0x00092440','r1_native_sync_signal'),('0x00045c20','r1_native_worker_park')]},
 **{entry:(name,'native-tx/verification.json') for entry,name in [('0x00034064','r1_ble_tx_queue_dispatch_type0'),('0x00034070','r1_ble_tx_queue_dispatch_type2'),('0x0003407c','r1_ble_tx_queue_dispatch_type1')]},
 '0x0004cb34':('r1_glasses_connection_handle_get','connection-handle/verification.json'),
 '0x0004cba4':('r1_phone_connection_handle_get','connection-handle/verification.json'),
 **{entry:(name,'native-task-lifecycle/verification.json') for entry,name in [('0x00043b8c','r1_thread_create_a'),('0x00043b74','r1_task_stop_668c'),('0x00046924','r1_thread_create_f'),('0x0004690c','r1_task_stop_6608'),('0x00046a44','r1_thread_create_g'),('0x00046a2c','r1_task_stop_66d8'),('0x00044ef0','r1_thread_create_b'),('0x00044ed8','r1_task_stop_65e0'),('0x0004509c','r1_thread_create_e'),('0x00045084','r1_task_stop_65bc')]},
 '0x0008d8fc':('r1_event_publish','native-events/verification.json'),
 '0x000924c0':('r1_event_bus_enqueue','native-events/verification.json'),
 '0x0004cb28':('r1_conn_field6_get','connection-handle/verification.json'),
 '0x00041e80':('r1_structured_log_cache_append','structured-cache/verification.json'),
 '0x00041c5c':('r1_structured_log_cache_copy','structured-cache-copy/verification.json'),
 '0x00027f6c':('r1_log_double_to_float_bits','structured-float/verification.json'),
 '0x00028078':('r1_log_round_float_bits','structured-float/verification.json'),
 **{entry:(name,'rtos-ticks/verification.json') for entry,name in [
 ('0x0007d28c','osKernelGetTickCount'),('0x00095f18','vPortValidateInterruptPriority'),
 ('0x000987a8','xTaskGetSchedulerState'),('0x000987c4','xTaskGetTickCount')]},
 **{entry:(name,'structured-time/verification.json') for entry,name in [
 ('0x000514bc','r1_structured_log_timestamp_adapter'),('0x0008ada4','r1_time_backend_timestamp'),
 ('0x0008ad40','r1_structured_log_local_timestamp')]},
 '0x00046fd4':('r1_structured_log_encode_format','structured-encode/verification.json'),
 '0x000277f0':('strlen','runtime/verification.json'),
 '0x00095cf4':('vPortEnterCritical','rtos-critical/verification.json'),
 '0x00095d24':('vPortExitCritical','rtos-critical/verification.json'),
 **{entry:(name,'structured-log/verification.json') for entry,name in [
 ('0x00091638','r1_structured_log_format'),('0x00091864','r1_structured_log_clock_available'),
 ('0x000590a0','r1_structured_log_export_active')]},
 **{entry:(name,'board-seams/verification.json') for entry,name in [
 ('0x0004e5bc','r1_adc_error'),('0x000914ec','r1_structured_log_mode_get'),
 ('0x000784f0','r1_st25_delay_ms')]},
 '0x000277ae':('memset','runtime/verification.json'),
 '0x000277fe':('strcmp','runtime/verification.json'),
 '0x000277aa':('__aeabi_memclr','runtime/verification.json'),
 **{entry:(name,'adc/sdk-execution.json') for entry,name in [
 ('0x0007af7c','nrfx_saadc_init'),('0x0007aeac','nrfx_saadc_channel_init'),
 ('0x0007af38','nrfx_saadc_channel_uninit'),('0x0007b150','nrfx_saadc_uninit')]},
 **{entry:(name,'adc/verification.json') for entry,name in [
 ('0x0005493c','r1_named_adc_register_all'),('0x00054864','r1_named_adc_open'),
 ('0x000548f0','r1_named_adc_sample'),('0x000547f4','r1_named_adc_close')]},
 **{entry:(name,'gpio/sdk-execution.json') for entry,name in [
 ('0x0007a73c','nrfx_gpiote_in_event_disable'),('0x0007a784','nrfx_gpiote_in_event_enable'),
 ('0x0007a81c','nrfx_gpiote_in_init'),('0x0007a8ec','nrfx_gpiote_in_uninit'),
 ('0x0007a94c','nrfx_gpiote_init'),('0x0007aa18','nrfx_gpiote_is_init')]},
 **{entry:(name,'gpio/verification.json') for entry,name in [
 ('0x00054c24','r1_named_gpio_register_all'),('0x00054afc','r1_named_gpio_callback'),
 ('0x00054ed0','r1_named_gpio_read'),('0x00054b40','r1_named_gpio_close'),
 ('0x00054b90','r1_named_gpio_open'),('0x0006ed94','r1_named_gpio_irq_dispatch')]},
 '0x0007a6dc':('r1_twi_delay_busy','software-twi/delay-verification.json'),
 '0x0007a6ec':('r1_twi_delay_busy','software-twi/delay-verification.json'),
 '0x0007081c':('r1_twi_delay_noop','software-twi/delay-verification.json'),
 '0x00054af0':('r1_twi_delay_noop','software-twi/delay-verification.json'),
 '0x0005547c':('r1_stock_i2c2_read','software-twi/adapter-verification.json'),
 '0x000554b0':('r1_stock_i2c3_read','software-twi/adapter-verification.json'),
 '0x000554e4':('r1_stock_i2c4_read','software-twi/adapter-verification.json'),
 '0x00055518':('r1_stock_i2c5_read','software-twi/adapter-verification.json'),
 '0x00055dbc':('r1_stock_i2c2_write','software-twi/adapter-verification.json'),
 '0x00055e40':('r1_stock_i2c3_write','software-twi/adapter-verification.json'),
 '0x00055ec4':('r1_stock_i2c4_write','software-twi/adapter-verification.json'),
 '0x00055f5c':('r1_stock_i2c5_write','software-twi/adapter-verification.json'),
 '0x00055330':('r1_stock_i2c2_open','software-twi/lifecycle-verification.json'),
 '0x00055360':('r1_stock_i2c3_open','software-twi/lifecycle-verification.json'),
 '0x00055390':('r1_stock_i2c4_open','software-twi/lifecycle-verification.json'),
 '0x000553e4':('r1_stock_i2c5_open','software-twi/lifecycle-verification.json'),
 '0x000551e8':('r1_stock_i2c2_close','software-twi/lifecycle-verification.json'),
 '0x0005520c':('r1_stock_i2c3_close','software-twi/lifecycle-verification.json'),
 '0x00055230':('r1_stock_i2c4_close','software-twi/lifecycle-verification.json'),
 '0x00055254':('r1_stock_i2c5_close','software-twi/lifecycle-verification.json'),
 '0x00079194':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x0007945c':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790bc':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079062':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00078fe4':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793b0':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791a8':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079470':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790d0':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079074':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00078ff6':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793c6':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791bc':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079484':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790e4':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079086':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00079008':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793dc':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791d0':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079498':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790f8':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079098':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x0007901a':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793f2':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 **{entry:('r1_stock_i2c'+str(i+2)+'_register','i2c5/registry-bootstrap-verification.json') for i,entry in enumerate(('0x00056508','0x00056520','0x00056538','0x00056550'))},
 '0x000557f8':('software_twi_read_transaction_reg8','software-twi/transaction-verification.json'),
 '0x00055878':('software_twi_read_transaction_reg8','software-twi/transaction-verification.json'),
 '0x000558f8':('software_twi_read_transaction_reg16','software-twi/transaction-verification.json'),
 '0x00055988':('software_twi_read_transaction_reg16','software-twi/transaction-verification.json'),
 '0x000560dc':('software_twi_write_transaction_reg16_byte','software-twi/transaction-verification.json'),
 '0x0005613e':('software_twi_write_transaction_reg8','software-twi/transaction-verification.json'),
 '0x000561a0':('software_twi_write_transaction_reg8','software-twi/transaction-verification.json'),
 '0x00056202':('software_twi_write_transaction_reg16','software-twi/transaction-verification.json'),
 '0x00055a18':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055a56':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055a94':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055ad2':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055b10':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b3c':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b68':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b94':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055bc0':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c08':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c50':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c98':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055548':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x000555f4':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x000556a0':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x0005574c':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x00055fa4':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x00055ff2':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x00056040':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x0005608e':('software_twi_write_byte','software-twi/primitive-verification.json'),
 **{entry:('r1_stock_dispatch_'+suffix,'i2c5/registry-dispatch-verification.json') for entry,suffix in [
 ('0x00085d08','00'),('0x00085d1a','08'),('0x00085cba','0c'),('0x00085d2c','10'),
 ('0x00085da8','14'),('0x00085ccc','18'),('0x00085d46','20')]},
 **{entry:(name,'i2c5/registry-bootstrap-verification.json') for entry,name in [
 ('0x00085ce0','r1_stock_registry_find'),('0x00085d58','r1_stock_registry_register'),
 ('0x00050d3c','r1_vnfc_rect_adc_handle_cache'),('0x00050464','r1_i2c5_nfc_resource_registration')]},
 **{entry:(name,'i2c5/verification.json') for entry,name in [
 ('0x00050510','r1_i2c5_read_transfer'),('0x00050534','r1_i2c5_write_transfer'),
 ('0x000504c0','r1_i2c5_nfc_resource_release'),('0x000504d8','r1_i2c5_nfc_resource_acquire')]},
 **{entry:(name,'sensors/st25-bus-verification.json') for entry,name in [
 ('0x00044c58','r1_st25dvxxkc_bus_tick_get'),('0x00044c64','r1_st25dvxxkc_bus_deinitialize'),
 ('0x00044c6e','r1_st25dvxxkc_bus_initialize'),('0x00044c78','r1_st25dvxxkc_bus_is_ready'),
 ('0x00044c84','r1_st25dvxxkc_bus_read'),('0x00044c8a','r1_st25dvxxkc_bus_write')]},
 '0x0005d87c':('r1_stock_crc16_modbus','checksum-verification.json'),
 '0x0005d8a4':('r1_stock_crc32_update','checksum-verification.json'),
 '0x0005d8cc':('r1_stock_hash131','checksum-verification.json'),
 '0x00095bb8':('vApplicationGetIdleTaskMemory','rtos/static-memory-verification.json'),
 '0x00095bd0':('vApplicationGetTimerTaskMemory','rtos/static-memory-verification.json'),
 '0x00048b02':('r1_stock_two_pass','crypto/verification.json'),
 '0x000891a4':('r1_stock_two_pass_callback','crypto/verification.json'),
 '0x00098e22':('r1_stock_xor','crypto/verification.json')}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def functions(path):
    data=path.read_bytes();assert data[:6]==b'\x7fELF\x01\x01'
    offset=struct.unpack_from('<I',data,32)[0];size,count=struct.unpack_from('<HH',data,46)
    sections=[struct.unpack_from('<10I',data,offset+i*size) for i in range(count)]
    result=[]
    for section in sections:
        if section[1]!=2:continue
        strings=sections[section[6]];names=data[strings[4]:strings[4]+strings[5]]
        for at in range(section[4],section[4]+section[5],section[9]):
            name,_,extent,info,_,index=struct.unpack_from('<IIIBBH',data,at)
            if name and index and info&15==2:
                result.append((names[name:].split(b'\0',1)[0].decode(),extent))
    return result


def main():
    candidates=collections.defaultdict(list);input_reports={}
    for relative in REPORTS:
        path=BASE/relative;report=json.loads(path.read_text());input_reports[relative]=sha(path)
        for row in report['units']:
            if row.get('compiled',True) is False:continue
            source=Path(row['source']);source=source if source.is_absolute() else ROOT/source
            assert sha(source)==row['source_sha256'],source
            command=row['command'];obj=Path(command[command.index('-o')+1])
            assert sha(obj)==row['object_sha256'],obj
            for name,extent in functions(obj):
                candidates[name].append(dict(source=str(source.relative_to(ROOT)),object=str(obj.relative_to(ROOT)),bytes=extent,report=relative))
    receipts={name:json.loads((BASE/name).read_text()) for name in ({name for _,name in VERIFIED.values()} | {'watchdog-startup/sdk-execution.json'})}
    app_hash='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    for name,receipt in receipts.items():
        assert receipt['application_sha256']==app_hash,name
    for path,expected in receipts['checksum-verification.json']['source_sha256'].items():
        if Path(path).suffix in ('.c','.h','.inc'):
            assert sha(ROOT/path)==expected,path
    static=receipts['rtos/static-memory-verification.json']
    assert sha(ROOT/'r1/components/rtos/static_task_memory.c')==static['source_sha256']
    assert sha(BASE/'rtos/11_static_task_memory.o')==static['object_sha256']
    assert sha(BASE/'crypto/two-pass.bin')==receipts['crypto/verification.json']['candidate_binary_sha256']
    st25=receipts['sensors/st25-bus-verification.json']
    assert sha(ROOT/'r1/components/st25/stock_bus_bindings.c')==st25['source_sha256']
    assert sha(ROOT/'r1/components/st25/stock_bus_bindings.h')==st25['binding_header_sha256']
    assert sha(BASE/'sensors/r1-st25-stock-bus.o')==st25['object_sha256']
    i2c5=receipts['i2c5/verification.json']
    assert sha(BASE/'i2c5/report.json')==i2c5['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==i2c5['relocatable_sha256']
    bootstrap=receipts['i2c5/registry-bootstrap-verification.json']
    assert sha(BASE/'i2c5/report.json')==bootstrap['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==bootstrap['relocatable_sha256']
    assert sha(ROOT/bootstrap['runtime_archive'])==bootstrap['runtime_archive_sha256']
    dispatch=receipts['i2c5/registry-dispatch-verification.json']
    assert sha(BASE/'i2c5/report.json')==dispatch['integration_report_sha256']
    assert sha(BASE/'i2c5/stock_registry.o')==dispatch['object_sha256']
    for twi_name in ('primitive-verification.json','transaction-verification.json'):
        twi=receipts['software-twi/'+twi_name]
        assert sha(BASE/'report.json')==twi['source_report_sha256']
        assert sha(ROOT/twi['source'])==twi['source_sha256']
        assert sha(ROOT/twi['object'])==twi['object_sha256']
        assert sha(ROOT/'r1/reconstructed/software_twi/software_twi.h')==twi['header_sha256']
    config=json.loads((BASE/'software-twi/board-configuration-verification.json').read_text())
    assert config['application_sha256']==app_hash
    assert sha(BASE/'report.json')==config['source_report_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==config['stock_initialization_sha256']
    assert sha(ROOT/'r1/reconstructed/software_twi/software_twi.c')==config['source_sha256']
    gpio=receipts['software-twi/gpio-verification.json']
    gpio_report=json.loads((BASE/'software-twi/gpio-report.json').read_text())
    assert sha(BASE/'software-twi/gpio-report.json')==gpio['gpio_report_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==gpio['stock_initialization_sha256']
    assert sha(BASE/'software-twi/sdk_gpio.o')==gpio['object_sha256']
    for path,digest in gpio_report['inputs'].items():assert sha(ROOT/path)==digest,path
    lifecycle=receipts['software-twi/lifecycle-verification.json']
    assert sha(BASE/'i2c5/report.json')==lifecycle['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==lifecycle['relocatable_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==lifecycle['stock_initialization_sha256']
    adapters=receipts['software-twi/adapter-verification.json']
    assert sha(BASE/'i2c5/report.json')==adapters['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==adapters['relocatable_sha256']
    delays=receipts['software-twi/delay-verification.json']
    assert sha(BASE/'software-twi/gpio-report.json')==delays['gpio_report_sha256']
    assert sha(BASE/'software-twi/sdk_gpio.o')==delays['object_sha256']
    native=json.loads((BASE/'software-twi/native-initialization-verification.json').read_text())
    assert native['application_sha256']==app_hash
    assert sha(BASE/'i2c5/report.json')==native['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==native['relocatable_sha256']
    null_buffers=json.loads((BASE/'software-twi/null-buffer-verification.json').read_text())
    assert null_buffers['application_sha256']==app_hash
    assert sha(BASE/'i2c5/report.json')==null_buffers['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==null_buffers['relocatable_sha256']
    assert null_buffers['fault_comparisons']>0
    named=receipts['gpio/verification.json']
    assert sha(BASE/'gpio/report.json')==named['gpio_report_sha256']
    assert sha(BASE/'i2c5/report.json')==named['integration_report_sha256']
    assert sha(BASE/'gpio/stock_named_gpio.o')==named['object_sha256']
    named_report=json.loads((BASE/'gpio/report.json').read_text())
    for path,digest in {**named_report['headers'],**named_report['inputs']}.items():assert sha(ROOT/path)==digest,path
    gpio_link=json.loads((BASE/'gpio/integration-report.json').read_text())
    assert sha(BASE/'gpio/gpio-native-integration.o')==gpio_link['relocatable_sha256']
    assert sha(BASE/'i2c5/report.json')==gpio_link['i2c5_report_sha256']
    assert sha(BASE/'application-sdk/report.json')==gpio_link['sdk_report_sha256']
    assert sha(BASE/'application-sdk/39_nrfx_gpiote.o')==gpio_link['gpiote_object_sha256']
    assert sha(BASE/'gpio/gpiote_layout_probe.c')==gpio_link['layout_probe_sha256']
    sdk_execution=receipts['gpio/sdk-execution.json']
    assert sha(BASE/'gpio/integration-report.json')==sdk_execution['integration_report_sha256']
    assert sha(BASE/'gpio/gpio-native-integration.o')==sdk_execution['relocatable_sha256']
    adc=receipts['adc/verification.json']
    assert sha(BASE/'adc/report.json')==adc['adc_report_sha256']
    assert sha(BASE/'i2c5/report.json')==adc['integration_report_sha256']
    assert sha(BASE/'adc/stock_named_adc.o')==adc['object_sha256']
    adc_report=json.loads((BASE/'adc/report.json').read_text())
    for path,digest in adc_report['inputs'].items():assert sha(ROOT/path)==digest,path
    adc_link=json.loads((BASE/'adc/integration-report.json').read_text())
    assert sha(BASE/'adc/adc-native-integration.o')==adc_link['relocatable_sha256']
    assert sha(BASE/'application-sdk/report.json')==adc_link['sdk_report_sha256']
    assert sha(BASE/'i2c5/report.json')==adc_link['transport_report_sha256']
    assert sha(BASE/'application-sdk/41_nrfx_saadc.o')==adc_link['sdk_object_sha256']
    adc_execution=receipts['adc/sdk-execution.json']
    assert sha(BASE/'adc/integration-report.json')==adc_execution['integration_report_sha256']
    assert sha(BASE/'adc/adc-native-integration.o')==adc_execution['relocatable_sha256']
    board=json.loads((BASE/'board/report.json').read_text())
    assert sha(BASE/'board/native-board.o')==board['relocatable_sha256']
    for path,digest in board['input_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in board['objects'].items():assert sha(ROOT/path)==digest,path
    board_test=json.loads((BASE/'board/verification.json').read_text())
    assert board_test['application_sha256']==app_hash
    assert sha(BASE/'board/report.json')==board_test['board_report_sha256']
    assert sha(BASE/'board/native-board.o')==board_test['relocatable_sha256']
    memory=receipts['runtime/verification.json']
    assert sha(BASE/'runtime/report.json')==memory['runtime_report_sha256']
    assert sha(BASE/'runtime/memory-runtime.o')==memory['relocatable_sha256']
    memory_report=json.loads((BASE/'runtime/report.json').read_text())
    for path,digest in memory_report['inputs'].items():assert sha(ROOT/path)==digest,path
    seams=receipts['board-seams/verification.json']
    assert sha(BASE/'board-seams/report.json')==seams['report_sha256']
    assert sha(BASE/'board-seams/stock_seams.o')==seams['object_sha256']
    assert sha(BASE/'software-twi/gpio-report.json')==seams['gpio_report_sha256']
    seam_report=json.loads((BASE/'board-seams/report.json').read_text())
    for path,digest in seam_report['inputs'].items():assert sha(ROOT/path)==digest,path
    structured=receipts['structured-log/verification.json']
    assert sha(BASE/'structured-log/report.json')==structured['report_sha256']
    assert sha(BASE/'structured-log/structured_log.o')==structured['object_sha256']
    assert sha(BASE/'board-seams/report.json')==structured['seam_report_sha256']
    log_report=json.loads((BASE/'structured-log/report.json').read_text())
    for path,digest in log_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical=receipts['rtos-critical/verification.json']
    assert sha(BASE/'rtos-critical/report.json')==critical['report_sha256']
    assert sha(BASE/'rtos-critical/critical-only.o')==critical['selected_object_sha256']
    critical_report=json.loads((BASE/'rtos-critical/report.json').read_text())
    for path,digest in critical_report['inputs'].items():assert sha(ROOT/path)==digest,path
    ticks=receipts['rtos-ticks/verification.json']
    assert sha(BASE/'rtos-ticks/report.json')==ticks['report_sha256']
    assert sha(BASE/'rtos-ticks/ticks-only.o')==ticks['selected_object_sha256']
    ticks_report=json.loads((BASE/'rtos-ticks/report.json').read_text())
    assert ticks_report['port_report_sha256']==sha(BASE/'rtos-critical/report.json')
    for path,digest in ticks_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical_log=json.loads((BASE/'structured-log/critical-integration-verification.json').read_text())
    assert critical_log['application_sha256']==app_hash and critical_log['actual_critical_functions']
    assert sha(BASE/'rtos-critical/report.json')==critical_log['critical_report_sha256']
    assert sha(BASE/'structured-log/report.json')==critical_log['report_sha256']
    encode=receipts['structured-encode/verification.json']
    assert sha(BASE/'structured-encode/report.json')==encode['report_sha256']
    assert sha(BASE/'structured-encode/structured_encode.o')==encode['object_sha256']
    for path,digest in encode['provider_reports'].items():assert sha(BASE/path)==digest,path
    encode_report=json.loads((BASE/'structured-encode/report.json').read_text())
    for path,digest in encode_report['inputs'].items():assert sha(ROOT/path)==digest,path
    time=receipts['structured-time/verification.json']
    assert sha(BASE/'structured-time/report.json')==time['report_sha256']
    assert sha(BASE/'structured-time/structured_time.o')==time['object_sha256']
    assert sha(BASE/'i2c5/report.json')==time['registry_report_sha256']
    assert sha(BASE/'runtime/report.json')==time['runtime_report_sha256']
    time_report=json.loads((BASE/'structured-time/report.json').read_text())
    for path,digest in time_report['inputs'].items():assert sha(ROOT/path)==digest,path
    floating=receipts['structured-float/verification.json']
    assert sha(BASE/'structured-float/report.json')==floating['report_sha256']
    assert sha(BASE/'structured-float/structured_float.o')==floating['object_sha256']
    float_report=json.loads((BASE/'structured-float/report.json').read_text())
    for path,digest in float_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for name,object_name in (('structured-cache','structured_cache.o'),('structured-cache-copy','structured_cache_copy.o')):
        receipt=receipts[name+'/verification.json'];report_path=BASE/(name+'/report.json');report=json.loads(report_path.read_text())
        assert sha(report_path)==receipt['report_sha256']
        assert sha(BASE/(name+'/'+object_name))==receipt['object_sha256']
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
        for path,digest in receipt.get('provider_reports',{}).items():assert sha(BASE/path)==digest,path
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
    for name in ('structured-encode/float-integration-verification.json','structured-cache/copy-integration-verification.json'):
        receipt=json.loads((BASE/name).read_text());component=name.split('/')[0]
        assert receipt['application_sha256']==app_hash
        assert sha(BASE/(component+'/report.json'))==receipt['report_sha256']
        for path,digest in receipt['provider_reports'].items():assert sha(BASE/path)==digest,path
    for name,object_name in (('native-events','native_events.o'),('connection-handle','connection_handle.o'),('native-tx','native_tx.o'),('native-task-lifecycle','native_task_lifecycle.o'),('native-tasks','native_tasks.o'),('native-sync','native_sync.o'),('native-watchdog','native_watchdog.o'),('native-event-dispatch','native_event_dispatch.o')):
        receipt=receipts[name+'/verification.json'];report_path=BASE/(name+'/report.json');report=json.loads(report_path.read_text())
        assert sha(report_path)==receipt['report_sha256']
        assert sha(BASE/(name+'/'+object_name))==receipt['object_sha256']
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
    for name in ('native-tx','native-task-lifecycle','native-tasks'):
        for path,digest in receipts[name+'/verification.json']['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'native-task-lifecycle/configuration-evidence.json')==receipts['native-task-lifecycle/verification.json']['configuration_sha256']
    task_sync=json.loads((BASE/'native-tasks/sync-integration-verification.json').read_text())
    assert task_sync['application_sha256']==app_hash and task_sync['actual_sync_bodies']
    assert sha(BASE/'native-tasks/report.json')==task_sync['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==task_sync['object_sha256']
    for path,digest in task_sync['provider_reports'].items():assert sha(BASE/path)==digest,path
    watchdog=receipts['native-watchdog/verification.json'];watchdog_report=json.loads((BASE/'native-watchdog/report.json').read_text())
    assert sha(BASE/'native-watchdog/current-task-only.o')==watchdog['selected_current_task_sha256']==watchdog_report['selected_current_task_sha256']
    assert sha(BASE/'rtos-ticks/report.json')==watchdog_report['upstream_report_sha256']
    watchdog_tasks=json.loads((BASE/'native-tasks/watchdog-integration-verification.json').read_text())
    assert watchdog_tasks['application_sha256']==app_hash and watchdog_tasks['actual_watchdog_bodies'] and watchdog_tasks['actual_sync_bodies']
    assert sha(BASE/'native-tasks/report.json')==watchdog_tasks['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==watchdog_tasks['object_sha256']
    for path,digest in watchdog_tasks['provider_reports'].items():assert sha(BASE/path)==digest,path
    startup_report_path=BASE/'watchdog-startup/report.json';startup_report=json.loads(startup_report_path.read_text())
    assert sha(BASE/'application-sdk/report.json')==startup_report['sdk_report_sha256']
    assert sha(BASE/'application-sdk/44_nrfx_wdt.o')==startup_report['sdk_object_sha256']
    for path,digest in startup_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for name in ('watchdog-startup/manager-verification.json','watchdog-startup/device-verification.json','watchdog-startup/sdk-execution.json'):
        receipt=receipts[name];assert sha(startup_report_path)==receipt['report_sha256']
        if 'relocatable_sha256' in receipt:assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==startup_report['relocatable_sha256']==receipt['relocatable_sha256']
        if 'registry_report_sha256' in receipt:assert sha(BASE/'i2c5/report.json')==receipt['registry_report_sha256']
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
        if 'watchdog_report_sha256' in receipt:assert sha(BASE/'native-watchdog/report.json')==receipt['watchdog_report_sha256']
    integer=receipts['integer-runtime/verification.json']
    assert sha(BASE/'integer-runtime/report.json')==integer['runtime_report_sha256']
    assert sha(BASE/'integer-runtime/integer-runtime.o')==integer['relocatable_sha256']
    for path,digest in json.loads((BASE/'integer-runtime/report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    integrated=json.loads((BASE/'watchdog-startup/sdk-division-integration.json').read_text())
    assert integrated['application_sha256']==app_hash and integrated['actual_sdk_executed'] and integrated['actual_integer_runtime_executed']
    assert sha(BASE/'integer-runtime/report.json')==integrated['integer_runtime_report_sha256']
    assert sha(startup_report_path)==integrated['report_sha256']
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==integrated['relocatable_sha256']
    assert sha(BASE/'runtime/report.json')==integrated['runtime_report_sha256']
    assert sha(BASE/'i2c5/report.json')==integrated['registry_report_sha256']
    sdk_critical=receipts['sdk-critical/verification.json'];critical_path=BASE/'sdk-critical/report.json';critical_report=json.loads(critical_path.read_text())
    assert sha(critical_path)==sdk_critical['report_sha256']
    assert sha(BASE/'sdk-critical/critical-only.o')==sdk_critical['selected_object_sha256']==critical_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==critical_report['sdk_report_sha256']
    for path,digest in critical_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical_integration=json.loads((BASE/'watchdog-startup/sdk-critical-integration.json').read_text())
    assert critical_integration['application_sha256']==app_hash and critical_integration['actual_sdk_executed'] and critical_integration['actual_integer_runtime_executed'] and critical_integration['actual_critical_regions_executed']
    for path,field in (('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('watchdog-startup/report.json','report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==critical_integration[field],path
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==critical_integration['relocatable_sha256']
    ticks_integration=json.loads((BASE/'watchdog-startup/sdk-ticks-integration.json').read_text())
    assert ticks_integration['application_sha256']==app_hash and ticks_integration['actual_sdk_executed'] and ticks_integration['actual_integer_runtime_executed'] and ticks_integration['actual_critical_regions_executed'] and ticks_integration['actual_tick_getter_executed']
    for path,field in (('rtos-ticks/report.json','ticks_report_sha256'),('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('watchdog-startup/report.json','report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==ticks_integration[field],path
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==ticks_integration['relocatable_sha256']
    assert board_test['nvic_initial_zero_bytes_compared']==12 and board_test['rtos_tick_critical_initial_zero_bytes_compared']==21
    log_report_path=BASE/'watchdog-logging/report.json';log_report=json.loads(log_report_path.read_text())
    assert sha(BASE/'watchdog-startup/report.json')==log_report['parent_report_sha256']
    assert sha(BASE/'application-sdk/report.json')==log_report['sdk_report_sha256']
    assert sha(BASE/'board-seams/report.json')==log_report['getter_report_sha256']
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==log_report['selected_getter_sha256']
    for path,digest in log_report['inputs'].items():assert sha(ROOT/path)==digest,path
    log_check=receipts['watchdog-logging/verification.json']
    assert sha(log_report_path)==log_check['report_sha256'] and log_check['native_sdk_logging_executed']
    assert sha(BASE/'watchdog-logging/native-watchdog-logging.o')==log_report['relocatable_sha256']==log_check['relocatable_sha256']
    for path,field in (('rtos-ticks/report.json','ticks_report_sha256'),('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==log_check[field],path
    strings=receipts['watchdog-logging/strerror-verification.json']
    assert sha(log_report_path)==strings['report_sha256'] and sha(BASE/'watchdog-logging/nrf_strerror.o')==strings['object_sha256']
    assert log_check['mode_values_tested']==256 and log_check['mode_transition_sequences_tested']==512
    assert board_test['watchdog_log_descriptor_bytes_compared']==log_check['descriptor_initial_bytes_compared']==87
    output_receipt=receipts['native-output/verification.json'];output_report_path=BASE/'native-output/report.json';output_report=json.loads(output_report_path.read_text())
    assert sha(output_report_path)==output_receipt['report_sha256']
    assert sha(BASE/'native-output/native_output.o')==output_receipt['object_sha256']
    for path,digest in output_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in output_receipt['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==output_receipt['selected_getter_sha256']
    assert board_test['output_descriptor_bytes_compared']==output_receipt['descriptor_bytes_compared']==68
    output_integration=json.loads((BASE/'native-tasks/output-integration-verification.json').read_text())
    assert output_integration['application_sha256']==app_hash and output_integration['actual_output_bodies'] and output_integration['actual_sync_bodies'] and output_integration['actual_watchdog_bodies']
    assert all(output_integration['output_execution_counts'].values())
    assert sha(BASE/'native-tasks/report.json')==output_integration['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==output_integration['object_sha256']
    for path,digest in output_integration['provider_reports'].items():assert sha(BASE/path)==digest,path
    sender=receipts['native-ble-send/verification.json'];sender_report_path=BASE/'native-ble-send/report.json';sender_report=json.loads(sender_report_path.read_text())
    assert sha(sender_report_path)==sender['report_sha256'] and sha(BASE/'native-ble-send/native_ble_send.o')==sender['object_sha256']
    assert sha(BASE/'connection-handle/report.json')==sender['connection_report_sha256']
    for path,digest in sender_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert board_test['ble_semaphore_initial_zero_bytes_compared']==sender['initial_semaphore_zero_bytes_compared']==8
    assert board['unresolved_data_anchors']['r1_native_bae8_service']=='0x20006504'
    sender_output=json.loads((BASE/'native-output/sender-integration-verification.json').read_text())
    assert sender_output['application_sha256']==app_hash and sender_output['actual_sender_executed'] and all(sender_output['sender_execution_counts'].values())
    assert sha(output_report_path)==sender_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==sender_output['object_sha256']
    for path,digest in sender_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==sender_output['selected_getter_sha256']
    sender_tasks=json.loads((BASE/'native-tasks/sender-integration-verification.json').read_text())
    assert sender_tasks['application_sha256']==app_hash and sender_tasks['actual_sender_executed'] and sender_tasks['actual_output_bodies'] and sender_tasks['actual_sync_bodies'] and sender_tasks['actual_watchdog_bodies']
    assert all(sender_tasks['output_execution_counts'].values())
    assert sha(BASE/'native-tasks/report.json')==sender_tasks['report_sha256'] and sha(BASE/'native-tasks/native_tasks.o')==sender_tasks['object_sha256']
    for path,digest in sender_tasks['provider_reports'].items():assert sha(BASE/path)==digest,path
    bae8=receipts['native-bae8-send/verification.json'];bae8_path=BASE/'native-bae8-send/report.json';bae8_report=json.loads(bae8_path.read_text())
    assert sha(bae8_path)==bae8['report_sha256'] and sha(BASE/'native-bae8-send/native_bae8_send.o')==bae8['object_sha256']
    assert sha(BASE/'application-sdk/report.json')==bae8_report['sdk_report_sha256']
    for path,digest in bae8_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bae8['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==bae8['selected_getter_sha256']
    assert board_test['bae8_descriptor_bytes_compared']==bae8['descriptor_bytes_compared']==806
    assert bae8['svc174_calls']>0
    bae8_output=json.loads((BASE/'native-output/bae8-integration-verification.json').read_text())
    assert bae8_output['application_sha256']==app_hash and bae8_output['actual_sender_executed'] and bae8_output['actual_bae8_executed'] and bae8_output['svc174_calls']>0
    assert sha(output_report_path)==bae8_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==bae8_output['object_sha256']
    for path,digest in bae8_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==bae8_output['selected_getter_sha256']
    context=receipts['sdk-link-context/verification.json'];context_path=BASE/'sdk-link-context/report.json';context_report=json.loads(context_path.read_text())
    assert sha(context_path)==context['report_sha256'] and sha(BASE/'sdk-link-context/blcm_link_ctx_get.o')==context['object_sha256']
    assert sha(BASE/'application-sdk/report.json')==context_report['sdk_report_sha256']
    for path,digest in context_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert board['provider_aliases']==context_report['provider_aliases']=={'r1_native_bae8_context_get':'blcm_link_ctx_get'}
    context_bae8=json.loads((BASE/'native-bae8-send/context-integration-verification.json').read_text())
    assert context_bae8['application_sha256']==app_hash and context_bae8['actual_link_context_executed'] and context_bae8['svc174_calls']>0
    assert sha(bae8_path)==context_bae8['report_sha256'] and sha(BASE/'native-bae8-send/native_bae8_send.o')==context_bae8['object_sha256']
    for path,digest in context_bae8['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==context_bae8['selected_getter_sha256']
    context_output=json.loads((BASE/'native-output/context-integration-verification.json').read_text())
    assert context_output['application_sha256']==app_hash and context_output['actual_link_context_executed'] and context_output['actual_sender_executed'] and context_output['actual_bae8_executed'] and context_output['svc174_calls']>0
    assert sha(output_report_path)==context_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==context_output['object_sha256']
    for path,digest in context_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==context_output['selected_getter_sha256']
    index=receipts['sdk-connection-index/verification.json'];index_path=BASE/'sdk-connection-index/report.json';index_report=json.loads(index_path.read_text())
    assert sha(index_path)==index['report_sha256'] and sha(BASE/'sdk-connection-index/connection-index-only.o')==index['selected_object_sha256']==index_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==index_report['sdk_report_sha256']
    for path,digest in index_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sha(BASE/'runtime/report.json')==index['memory_report_sha256']
    assert index['authenticated_native_reset_bytes']==index_report['authenticated_native_reset_bytes']==124
    assert board_test['connection_state_candidate_initial_zero_bytes_compared']==index['candidate_state_initial_zero_bytes_compared']==124
    index_lookup=json.loads((BASE/'sdk-link-context/index-integration-verification.json').read_text())
    assert index_lookup['application_sha256']==app_hash and index_lookup['actual_connection_index_executed']
    assert sha(index_path)==index_lookup['index_report_sha256'] and sha(context_path)==index_lookup['report_sha256'] and sha(BASE/'sdk-link-context/blcm_link_ctx_get.o')==index_lookup['object_sha256']
    for parent,object_name in (('native-bae8-send','native_bae8_send.o'),('native-output','native_output.o')):
        check=json.loads((BASE/parent/'index-integration-verification.json').read_text())
        assert check['application_sha256']==app_hash and check['actual_connection_index_executed'] and check['actual_link_context_executed'] and check['svc174_calls']>0
        assert sha(BASE/parent/'report.json')==check['report_sha256'] and sha(BASE/parent/object_name)==check['object_sha256']
        for path,digest in check['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert sha(BASE/'watchdog-logging/mode-getter-only.o')==check['selected_getter_sha256']
    events=receipts['sdk-connection-events/verification.json'];events_path=BASE/'sdk-connection-events/report.json';events_report=json.loads(events_path.read_text())
    assert sha(events_path)==events['report_sha256'] and sha(BASE/'sdk-connection-events/connection-events.o')==events['selected_object_sha256']==events_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==events_report['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==events['memory_report_sha256']
    for path,digest in events_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert events['injected_failed_store_exclusives']>0 and board_test['registry_observer_record_bytes_pointer_normalized']==8
    events_index=json.loads((BASE/'sdk-connection-events/index-verification.json').read_text())
    assert events_index['application_sha256']==app_hash and events_index['events_provider'] and sha(events_path)==events_index['report_sha256']
    assert sha(BASE/'sdk-connection-events/connection-events.o')==events_index['selected_object_sha256']
    assert sha(BASE/'runtime/report.json')==events_index['memory_report_sha256']
    for parent,object_name in (('native-bae8-send','native_bae8_send.o'),('native-output','native_output.o')):
        check=json.loads((BASE/parent/'events-integration-verification.json').read_text())
        assert check['application_sha256']==app_hash and check['events_provider'] and check['actual_registry_events_executed'] and check['actual_connection_index_executed'] and check['svc174_calls']>0
        assert sha(BASE/parent/'report.json')==check['report_sha256'] and sha(BASE/parent/object_name)==check['object_sha256']
        for path,digest in check['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert sha(BASE/'watchdog-logging/mode-getter-only.o')==check['selected_getter_sha256']
    dispatch_path=BASE/'sdk-ble-dispatch/report.json';dispatch=json.loads(dispatch_path.read_text())
    for receipt_name in ('verification.json','iterator-verification.json','registry-integration-verification.json'):
        check=json.loads((dispatch_path.parent/receipt_name).read_text())
        assert check['application_sha256']==app_hash and check['report_sha256']==sha(dispatch_path)
        assert check['comparisons']>0
        if 'selected_object_sha256' in check:
            assert check['selected_object_sha256']==dispatch['selected_object_sha256']==sha(dispatch_path.parent/'ble-dispatch.o')
        else:assert check['object_sha256']==sha(dispatch_path.parent/'nrf_section_iter.o')
        for path,digest in check.get('provider_reports',{}).items():assert sha(BASE/path)==digest,path
        if receipt_name=='registry-integration-verification.json':assert check['actual_registry_handler'] and check['observer_calls']>0
    for path,digest in dispatch['inputs'].items():assert sha(ROOT/path)==digest,path
    assert board_test['ble_observer_table_bytes_pointer_normalized']==96
    assert board_test['ble_observer_range_set_bytes_compared']==44 and board_test['ble_stack_initial_zero_bytes_compared']==1
    qwr_path=BASE/'sdk-qwr/report.json';qwr=json.loads(qwr_path.read_text());qwr_test=receipts['sdk-qwr/verification.json']
    assert qwr_test['report_sha256']==sha(qwr_path) and qwr_test['selected_object_sha256']==qwr['selected_object_sha256']==sha(qwr_path.parent/'qwr.o')
    assert sha(BASE/'application-sdk/report.json')==qwr['sdk_report_sha256']
    for path,digest in qwr['inputs'].items():assert sha(ROOT/path)==digest,path
    assert qwr_test['invalid_bool_byte_2_diverges'] and qwr_test['context_initial_zero_bytes_compared']==36 and qwr_test['svc_calls']>0
    assert board_test['qwr_context_initial_zero_bytes_compared']==36
    qwr_integration=json.loads((BASE/'sdk-ble-dispatch/qwr-integration-verification.json').read_text())
    assert qwr_integration['application_sha256']==app_hash and qwr_integration['report_sha256']==sha(dispatch_path)
    assert qwr_integration['selected_object_sha256']==dispatch['selected_object_sha256'] and qwr_integration['actual_qwr_handler'] and qwr_integration['actual_registry_handler'] and qwr_integration['qwr_svc_calls']>0
    for path,digest in qwr_integration['provider_reports'].items():assert sha(BASE/path)==digest,path
    gatt_path=BASE/'sdk-gatt/report.json';gatt=json.loads(gatt_path.read_text());gatt_test=receipts['sdk-gatt/verification.json']
    assert gatt_test['report_sha256']==sha(gatt_path) and gatt_test['selected_object_sha256']==gatt['selected_object_sha256']==sha(gatt_path.parent/'gatt-init.o')
    assert sha(BASE/'application-sdk/report.json')==gatt['sdk_report_sha256']
    for path,digest in gatt['inputs'].items():assert sha(ROOT/path)==digest,path
    assert gatt_test['context_initial_zero_bytes_compared']==36 and board_test['gatt_context_initial_zero_bytes_compared']==36
    assert not gatt_test['observer_contract_proven'] and not gatt['observer_selected'] and not gatt['role_split_proven']
    assert sum(not row['equivalent'] for row in gatt_test['observer_counterexamples'])==4
    native_gatt_path=BASE/'native-gatt/report.json';native_gatt=json.loads(native_gatt_path.read_text());native_gatt_test=receipts['native-gatt/verification.json']
    assert native_gatt_test['report_sha256']==sha(native_gatt_path) and native_gatt_test['object_sha256']==native_gatt['units'][0]['object_sha256']==sha(native_gatt_path.parent/'native_gatt_observer.o')
    assert sha(BASE/'application-sdk/report.json')==native_gatt['sdk_report_sha256']
    for path,digest in native_gatt['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in native_gatt_test['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert native_gatt_test['selected_getter_sha256']==sha(BASE/'watchdog-logging/mode-getter-only.o')
    assert native_gatt_test['strerror_object_sha256']==sha(BASE/'watchdog-logging/nrf_strerror.o')
    assert native_gatt_test['svc_calls']>0 and native_gatt_test['descriptor_bytes_compared']==board_test['gatt_log_descriptor_bytes_compared']
    gatt_dispatch=json.loads((BASE/'sdk-ble-dispatch/gatt-integration-verification.json').read_text())
    assert gatt_dispatch['application_sha256']==app_hash and gatt_dispatch['report_sha256']==sha(dispatch_path) and gatt_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert gatt_dispatch['actual_gatt_handler'] and gatt_dispatch['actual_qwr_handler'] and gatt_dispatch['actual_registry_handler'] and gatt_dispatch['gatt_svc_calls']>0
    for path,digest in gatt_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    advertising_path=BASE/'sdk-advertising/report.json';advertising=json.loads(advertising_path.read_text());advertising_test=receipts['sdk-advertising/verification.json']
    assert advertising_test['report_sha256']==sha(advertising_path) and advertising_test['selected_object_sha256']==advertising['selected_object_sha256']==sha(advertising_path.parent/'advertising.o')
    assert sha(BASE/'application-sdk/report.json')==advertising['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==advertising_test['memory_report_sha256']
    for path,digest in advertising['inputs'].items():assert sha(ROOT/path)==digest,path
    assert advertising_test['svc_calls']>0 and advertising_test['compatible_context_initial_zero_bytes_compared']==board_test['advertising_compatible_context_zero_bytes_compared']==2152
    assert not advertising['initialization_provider_selected']
    advertising_dispatch=json.loads((BASE/'sdk-ble-dispatch/advertising-integration-verification.json').read_text())
    assert advertising_dispatch['application_sha256']==app_hash and advertising_dispatch['report_sha256']==sha(dispatch_path) and advertising_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert advertising_dispatch['actual_advertising_handler'] and advertising_dispatch['actual_gatt_handler'] and advertising_dispatch['actual_qwr_handler'] and advertising_dispatch['actual_registry_handler'] and advertising_dispatch['advertising_svc_calls']>0
    for path,digest in advertising_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    advertising_init_path=BASE/'sdk-advertising-init/report.json';advertising_init=json.loads(advertising_init_path.read_text());advertising_init_test=receipts['sdk-advertising-init/verification.json']
    assert advertising_init_test['report_sha256']==sha(advertising_init_path) and advertising_init_test['selected_object_sha256']==advertising_init['selected_object_sha256']==sha(advertising_init_path.parent/'advertising.o')
    assert sha(BASE/'application-sdk/report.json')==advertising_init['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==advertising_init_test['memory_report_sha256']
    for path,digest in advertising_init['inputs'].items():assert sha(ROOT/path)==digest,path
    assert advertising_init['initialization_provider_selected'] and advertising_init_test['svc_calls']>0 and advertising_init_test['native_capacity_overrun_cases']>0
    advertising_legacy=json.loads((advertising_init_path.parent/'legacy-verification.json').read_text())
    assert advertising_legacy['application_sha256']==app_hash and advertising_legacy['report_sha256']==sha(advertising_init_path) and advertising_legacy['selected_object_sha256']==advertising_init['selected_object_sha256'] and advertising_legacy['memory_report_sha256']==sha(BASE/'runtime/report.json')
    advertising_init_dispatch=json.loads((BASE/'sdk-ble-dispatch/advertising-init-integration-verification.json').read_text())
    assert advertising_init_dispatch['application_sha256']==app_hash and advertising_init_dispatch['report_sha256']==sha(dispatch_path) and advertising_init_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert advertising_init_dispatch['actual_advertising_init'] and advertising_init_dispatch['advertising_init_calls']==2*advertising_init_dispatch['comparisons']
    for path,digest in advertising_init_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv' 
    output=[];counts=collections.Counter();families=collections.defaultdict(collections.Counter)
    for row in csv.DictReader(ownership.open()):
        contract=VERIFIED.get(row['entry']) if row['image']=='application' else None
        name=contract[0] if contract else row['upstream_symbol']
        matches=candidates.get(name,[])
        if contract and contract[1]=='sdk-advertising-init/verification.json':
            matches=[m for m in matches if m['report']=='sdk-advertising-init/report.json']
        if contract and contract[1]=='sdk-advertising/verification.json':
            matches=[m for m in matches if m['report']=='sdk-advertising/report.json']
        if contract and contract[1]=='native-gatt/verification.json':
            matches=[m for m in matches if m['report']=='native-gatt/report.json']
        if contract and contract[1]=='sdk-gatt/verification.json':
            matches=[m for m in matches if m['report']=='sdk-gatt/report.json']
        if contract and contract[1]=='sdk-qwr/verification.json':
            matches=[m for m in matches if m['report']=='sdk-qwr/report.json']
        if contract and contract[1].startswith('sdk-ble-dispatch/'):
            matches=[m for m in matches if m['report']=='sdk-ble-dispatch/report.json']
        if contract and contract[1]=='sdk-connection-events/verification.json':
            matches=[m for m in matches if m['report']=='sdk-connection-events/report.json']
        if contract and contract[1]=='sdk-connection-index/verification.json':
            matches=[m for m in matches if m['report']=='sdk-connection-index/report.json']
        if contract and contract[1]=='sdk-link-context/verification.json':
            matches=[m for m in matches if m['report']=='sdk-link-context/report.json']
        if contract and contract[1]=='native-bae8-send/verification.json':
            matches=[m for m in matches if m['report']=='native-bae8-send/report.json']
        if contract and contract[1]=='native-ble-send/verification.json':
            matches=[m for m in matches if m['report']=='native-ble-send/report.json']
        if contract and contract[1]=='native-output/verification.json':
            matches=[m for m in matches if m['report']=='native-output/report.json']
        if contract and contract[1] in ('watchdog-logging/verification.json','watchdog-logging/strerror-verification.json'):
            matches=[m for m in matches if m['report']=='watchdog-logging/report.json']
        if contract and contract[1]=='sdk-critical/verification.json':
            matches=[m for m in matches if m['report']=='sdk-critical/report.json']
        if contract and contract[1]=='integer-runtime/verification.json':
            matches=[m for m in matches if m['report']=='integer-runtime/report.json']
        if contract and contract[1]=='rtos-critical/verification.json':
            matches=[m for m in matches if m['report']=='rtos-critical/report.json']
        if contract and contract[1]=='rtos-ticks/verification.json':
            expected='rtos-critical/report.json' if name=='vPortValidateInterruptPriority' else 'rtos-ticks/report.json'
            matches=[m for m in matches if m['report']==expected]
        if contract and contract[1]=='native-watchdog/verification.json':
            matches=[m for m in matches if m['report']=='native-watchdog/report.json']
        if contract and contract[1]=='watchdog-startup/sdk-execution.json':
            matches=[m for m in matches if m['report']=='application-sdk/report.json']
        status='tested_contract_candidate' if contract and matches else 'compiled_symbol_hint' if matches else 'unresolved_source_route'
        if contract:
            assert matches and (BASE/contract[1]).is_file(),contract
        counts[status]+=1;families[row['provider_family']][status]+=1
        output.append(dict(image=row['image'],inventory_source=row['inventory_source'],entry=row['entry'],size=row['size'],
                           provider_family=row['provider_family'],source_symbol=row['upstream_symbol'],candidate_symbol=name,
                           status=status,candidate_sources=';'.join(sorted({m['source'] for m in matches})),
                           candidate_objects=';'.join(sorted({m['object'] for m in matches})),
                           candidate_reports=';'.join(sorted({m['report'] for m in matches})),
                           behavior_receipt=contract[1] if contract else '',instruction_identity_proven='false',
                           image_integration_proven='false'))
    with (BASE/'function-frontier.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    summary=dict(schema=1,ownership_ledger_sha256=sha(ownership),input_reports=input_reports,ownership_entries=len(output),
                 counts=dict(counts),providers={name:dict(count) for name,count in sorted(families.items())},
                 exact_instruction_matches_proven=0,image_integration_proven=False,
                 limitations=['Ownership ledger has 3326 entries from multiple inventories; the structural Ghidra corpus has 2972 functions. These are different scopes.',
                              'Name matches include local symbols and are routing hints, not ABI/body matches or source admission.',
                              'Tested contract candidates cover bounded inputs in cited receipts; they do not prove all input behavior or exact compiler output.',
                              'This audit verifies recorded source/object hashes; report-specific header/configuration authentication remains owned by each build target.'])
    (BASE/'function-frontier-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'Ownership entries accounted for: {len(output)}; statuses: {dict(counts)}')
    remaining=sorted(((count['unresolved_source_route'],name) for name,count in families.items()),reverse=True)
    print('Largest unresolved source routes:',remaining[:6])


if __name__=='__main__':main()
