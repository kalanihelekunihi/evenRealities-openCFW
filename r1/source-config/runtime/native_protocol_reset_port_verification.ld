PROVIDE(r1_fragment_message = 0x32409);
PROVIDE(r1_eus_ingress_plan_decode = 0x8316d);
PROVIDE(r1_structured_log_mode_get = 0x2000020d);
PROVIDE(r1_structured_log_format = 0x20000211);
PROVIDE(nrf_log_frontend_std_0 = 0x20000215);
PROVIDE(r1_native_delayed_schedule = 0x20000205);
PROVIDE(r1_event_publish = 0x20000209);
SECTIONS {
 .send 0x20006c20 (NOLOAD) : { *(.r1.protocol.send_hook) }
 .receive 0x20006c24 (NOLOAD) : { *(.r1.protocol.receive_hook) }
 .init_ring 0x83108 : { *(.r1.protocol_port.init_ring) }
 .init_sdk 0x83140 : { *(.r1.protocol_port.init_sdk) }
 .null_ring 0x8335c : { *(.r1.protocol_port.null_ring) }
 .null_sdk 0x83398 : { *(.r1.protocol_port.null_sdk) }
 .registered_ring 0x833cc : { *(.r1.protocol_port.registered_ring) }
 .registered_sdk 0x8340c : { *(.r1.protocol_port.registered_sdk) }
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .callback 0x83cd0 : { *(.r1.protocol.reset.callback) }
 .workspace 0x20019ef4 (NOLOAD) : { *(.r1.protocol.reset.workspace) }
 .sequence 0x20006b88 (NOLOAD) : { *(.r1.protocol.sequence) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
