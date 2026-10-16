PROVIDE(osMutexNew = 0x20000201);
PROVIDE(osMutexAcquire = 0x20000205);
PROVIDE(osMutexRelease = 0x20000209);
PROVIDE(r1_native_delayed_cancel = 0x2000020d);
PROVIDE(r1_native_delayed_schedule = 0x20000211);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .callback 0x4d2f0 : { *(.r1.ack.restart.callback) }
 .attributes 0x9a434 : { *(.r1.ack.mutex.attributes) }
 .name 0xc0228 : { *(.r1.ack.mutex.name) }
 .mutex 0x20006b8c (NOLOAD) : { *(.r1.ack.mutex) }
 .control 0x20019ea4 (NOLOAD) : { *(.r1.ack.mutex.control) }
 .workspace 0x20019ef4 (NOLOAD) : { *(.r1.protocol.reset.workspace) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
