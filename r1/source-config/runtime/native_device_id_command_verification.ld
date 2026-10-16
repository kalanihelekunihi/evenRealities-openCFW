PROVIDE(r1_native_device_id_read_boundary = 0x20000205);
PROVIDE(r1_protocol_response_send_0x100 = 0x20000209);
PROVIDE(r1_structured_log_mode_get = 0x2000020d);
PROVIDE(r1_structured_log_format = 0x20000211);
PROVIDE(nrf_log_frontend_std_2 = 0x20000215);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .default 0x9a56c : { *(.r1.device.id.default) }
 .ring 0x83ef0 : { *(.r1.device.id.ring) }
 .sdk 0x83f10 : { *(.r1.device.id.sdk) }
 .status 0x20006da5 : { *(.r1.device.id.status) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
