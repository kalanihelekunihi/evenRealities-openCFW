ENTRY(reset_entry)
SECTIONS { .vectors 0 : { KEEP(*(.vectors)) } .text 0x1000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }
