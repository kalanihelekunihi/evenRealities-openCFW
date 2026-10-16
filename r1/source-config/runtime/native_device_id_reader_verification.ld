SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) *(.r1.format.*) }
 .format 0x6abc8 : { *(.r1.device.id.format) }
 .cache_text 0xc0648 : { *(.r1.device.id.cache.text) }
 .valid 0x20006da4 : { *(.r1.device.id.cache.valid) }
 .pointer 0x20006e38 : { *(.r1.device.id.cache.pointer) }
 .length 0x20006e3c : { *(.r1.device.id.cache.length) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
