SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .context 0x20007a34 (NOLOAD) : { *(.r1.reset.retained.context) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
