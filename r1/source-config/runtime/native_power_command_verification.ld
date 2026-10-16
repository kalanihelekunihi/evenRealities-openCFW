PROVIDE(r1_protocol_send_flag_set_c = 0x20000205);
PROVIDE(osDelay = 0x20000209);
PROVIDE(r1_reset_trace_reboot_caller_write = 0x2000020d);
PROVIDE(r1_battery_voltage_get = 0x20000211);
PROVIDE(r1_time_backend_timestamp = 0x20000215);
PROVIDE(r1_kv_dev_info_fields_set = 0x20000219);
PROVIDE(osThreadFlagsSet = 0x2000021d);
PROVIDE(r1_structured_log_mode_get = 0x20000221);
PROVIDE(r1_structured_log_format = 0x20000225);
PROVIDE(nrf_log_frontend_std_0 = 0x20000229);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .ring 0xc0278 : { *(.r1.power.command.ring) }
 .sdk 0xc02c4 : { *(.r1.power.command.sdk) }
 .thread 0x20006548 : { *(.r1.battery.low.thread) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
