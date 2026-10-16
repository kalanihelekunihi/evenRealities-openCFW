PROVIDE(r1_protocol_send_response = 0x20000205);
PROVIDE(r1_event_publish = 0x20000209);
PROVIDE(r1_structured_log_mode_get = 0x2000020d);
PROVIDE(r1_structured_log_format = 0x20000211);
PROVIDE(nrf_log_frontend_std_4 = 0x20000215);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .ring 0x84adc : { *(.r1.profile.command.ring) }
 .sdk 0x84b08 : { *(.r1.profile.command.sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
