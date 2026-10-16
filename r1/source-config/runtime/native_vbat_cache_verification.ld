SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .name 0x91454 : { *(.r1.vbat.name) }
 .cache 0x200068a0 (NOLOAD) : { *(.r1.vbat.cache) }
 .head 0x20007680 (NOLOAD) : { *(.r1.registry.head) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
