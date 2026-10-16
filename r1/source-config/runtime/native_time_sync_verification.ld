PROVIDE(r1_native_delayed_cancel = 0x20000205);
PROVIDE(r1_protocol_time_timeout_callback = 0x84c83);
PROVIDE(r1_time_utc_offset_get = 0x20000209);
PROVIDE(r1_time_backend_timestamp = 0x2000020d);
PROVIDE(r1_event_publish = 0x20000211);
PROVIDE(r1_protocol_send_flag_set_c = 0x20000215);
PROVIDE(r1_protocol_ack_header_send = 0x20000219);
PROVIDE(r1_nv_recovery_needed_query_boundary = 0x2000021d);
PROVIDE(r1_phone_link_ready_query = 0x20000221);
PROVIDE(r1_native_nv_recovery_report_boundary = 0x20000225);
PROVIDE(r1_structured_log_mode_get = 0x20000229);
PROVIDE(r1_structured_log_format = 0x2000022d);
PROVIDE(nrf_log_frontend_std_0 = 0x20000231);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .lost_ring 0x847c8 : { *(.r1.time.sync.lost_ring) }
 .lost_sdk 0x847f0 : { *(.r1.time.sync.lost_sdk) }
 .valid_ring 0x84814 : { *(.r1.time.sync.valid_ring) }
 .valid_sdk 0x8483c : { *(.r1.time.sync.valid_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
