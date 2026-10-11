SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
