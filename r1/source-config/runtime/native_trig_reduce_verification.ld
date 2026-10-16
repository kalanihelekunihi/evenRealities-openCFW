SECTIONS {
 .text 0x1000000 : { *(.text*) }
 .r1.math.trig_reduce_table 0xbdb48 : { *(.r1.math.trig_reduce_table) }
 .r1.math.trig_reduce_coeff 0x3bc44 : { *(.r1.math.trig_reduce_coeff) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) *(.ARM.attributes*) }
}
