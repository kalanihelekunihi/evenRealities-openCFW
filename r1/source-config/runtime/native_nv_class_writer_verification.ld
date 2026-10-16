PROVIDE(r1_structured_log_mode_get = 0x20000201);
PROVIDE(r1_structured_log_format = 0x20000205);
PROVIDE(nrf_log_frontend_std_1 = 0x20000209);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .port 0x20006974 : { *(.r1.kv.port_slot) }
 .ring 0x917fc : { *(.r1.nv.class_writer.ring) }
 .sdk 0x91838 : { *(.r1.nv.class_writer.sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
