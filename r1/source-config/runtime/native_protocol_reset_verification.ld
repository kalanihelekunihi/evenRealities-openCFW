PROVIDE(r1_proto_port_init = 0x20000201);
PROVIDE(r1_native_delayed_schedule = 0x20000205);
PROVIDE(r1_event_publish = 0x20000209);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .callback 0x83cd0 : { *(.r1.protocol.reset.callback) }
 .workspace 0x20019ef4 (NOLOAD) : { *(.r1.protocol.reset.workspace) }
 .sequence 0x20006b88 (NOLOAD) : { *(.r1.protocol.sequence) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
