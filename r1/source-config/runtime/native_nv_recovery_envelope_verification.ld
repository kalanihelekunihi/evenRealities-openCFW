PROVIDE(r1_native_nv_recovery_command_dispatch = 0x20000201);
PROVIDE(r1_protocol_send_response = 0x20000205);
PROVIDE(r1_structured_log_mode_get = 0x20000209);
PROVIDE(r1_structured_log_format = 0x2000020d);
PROVIDE(nrf_log_frontend_std_0 = 0x20000211);
PROVIDE(nrf_log_frontend_std_3 = 0x20000215);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .null_ring 0x84208 : { *(.r1.nv.envelope.null_ring) }
 .null_sdk 0x84238 : { *(.r1.nv.envelope.null_sdk) }
 .fields_ring 0x84264 : { *(.r1.nv.envelope.fields_ring) }
 .fields_sdk 0x8429c : { *(.r1.nv.envelope.fields_sdk) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
