PROVIDE(r1_protocol_send_response = 0x20000201);
PROVIDE(r1_structured_log_mode_get = 0x20000205);
PROVIDE(r1_structured_log_format = 0x20000209);
PROVIDE(nrf_log_frontend_std_1 = 0x2000020d);
PROVIDE(r1_ble_thread_message_encode = 0x20000211);
PROVIDE(r1_phone_connection_role_assign = 0x20000215);
PROVIDE(osDelay = 0x20000219);
PROVIDE(osThreadFlagsSet = 0x2000021d);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .report_ring 0x8b87c : { *(.r1.control.report_ring) }
 .report_sdk 0x8b8b8 : { *(.r1.control.report_sdk) }
 .pair_ring 0x8436c : { *(.r1.control.pair_ring) }
 .pair_sdk 0x843a0 : { *(.r1.control.pair_sdk) }
 .report 0x200067a0 (NOLOAD) : { *(.r1.control.report.enabled) }
 .thread 0x20006570 (NOLOAD) : { *(.r1.control.service.thread) }
 .phone 0x200064ba (NOLOAD) : { *(.r1.connection.field8) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
