PROVIDE(r1_protocol_send_response = 0x20000201);
PROVIDE(r1_event_publish = 0x20000205);
PROVIDE(r1_service_health_report_set = 0x20000209);
SECTIONS {
 .health_table 0x9a454 : { *(.r1.protocol_commands.health) }
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
