PROVIDE(r1_kv_port = 0x20006974);
PROVIDE(r1_protocol_send_response = 0x20000205);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .class 0x20006ad8 : { *(.r1.serial.kv.class) }
 .handle 0x20007dfc : { *(.r1.serial.kv.handle) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
