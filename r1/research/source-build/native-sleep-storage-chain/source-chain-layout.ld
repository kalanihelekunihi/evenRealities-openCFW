SECTIONS { .b0 0x5b890 : { *(.text.r1_sleep_record_store) } .b1 0x8dc94 : { *(.text.r1_event_service_0008dc94) } .b2 0x5b2f8 : { *(.text.r1_sleep_erase_all) } .b3 0x8fe14 : { *(.text.r1_sleep_sector_count) } .b4 0x8dd88 : { *(.text.r1_event_service_0008dd88) } .b5 0x8fe28 : { *(.text.r1_sleep_sector_select) } .b6 0x8fc6c : { *(.text.r1_sleep_sector_fallback) } .b7 0x8fe98 : { *(.text.r1_sleep_sector_write) } .b8 0x901e4 : { *(.text.r1_sleep_sector_finalize) } .success 0xbfaf8 : { *(.r1.sleep.write.success) } .context 0x200067b4 : { *(.r1.sleep.sync.context) } .crc 0x5d87c : { *(.text) } .tables 0x995a8 : { *(.rodata) } /DISCARD/ : { *(.ARM.exidx*) } }
__aeabi_memclr = 0x277ab;
r1_structured_log_mode_get = 0x914ed;
r1_structured_log_format = 0x91639;
nrf_log_frontend_std_0 = 0x799c1;
nrf_log_frontend_std_1 = 0x799c9;
nrf_log_frontend_std_2 = 0x799d7;
nrf_log_frontend_std_3 = 0x799e7;
r1_health_event_notification_throttle = 0x8b139;
__start_log_const_data = 0xc441c;
