PROVIDE(r1_native_nv_recovery_merge_boundary = 0x20000219);
PROVIDE(r1_native_nv_recovery_report_boundary = 0x2000021d);
PROVIDE(nrf_log_frontend_std_2 = 0x20000221);
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
 .dispatch_ring 0x7c4bc : { *(.r1.nv.dispatch.ring) }
 .dispatch_sdk 0x7c4fc : { *(.r1.nv.dispatch.sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
