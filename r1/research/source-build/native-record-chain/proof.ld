SECTIONS { .b0 0x6c640 : { *(.text.r1_record12_validate) } .b1 0x6c66c : { *(.text.r1_event_service_0006c66c) } .b2 0x6c53c : { *(.text.r1_record12_apply) } .b3 0x73604 : { *(.text.r1_record12_persist) } .memcmp 0x1000000 : { *(.text.r1_native_memcmp) } /DISCARD/ : { *(.ARM.exidx*) } }
r1_structured_log_mode_get = 0x914ed;
r1_structured_log_format = 0x91639;
nrf_log_frontend_std_0 = 0x799c1;
r1_record12_reinitialize = 0x4c37d;
r1_kv_class_read = 0x73931;
r1_kv_class_write = 0x73969;
__start_log_const_data = 0xc441c; r1_device_id_once_status = 0x20006da0; r1_health_settings_kv_handle = 0x20007df0;
