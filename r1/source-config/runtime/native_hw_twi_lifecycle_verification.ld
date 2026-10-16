SECTIONS {
 .r1.hw_twi.template0 0x9a600 : { *(.r1.hw_twi.template0) }
 .r1.hw_twi.template1 0x9a620 : { *(.r1.hw_twi.template1) }
 .r1.hw_twi.primary 0x20006fe8 : { *(.r1.hw_twi.primary) }
 .r1.hw_twi.secondary 0x20007054 : { *(.r1.hw_twi.secondary) }
 .r1.hw_twi.name0 0xc06e4 : { *(.r1.hw_twi.name0) }
 .r1.hw_twi.name1 0xc06ec : { *(.r1.hw_twi.name1) }
 .text 0x1000000 : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
