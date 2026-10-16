SECTIONS { . = 0x01000000; .text : { *(.text*) *(.rodata*) } .r1.scatter.regions : { *(.r1.scatter.regions) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
