ENTRY(reset_entry)
stock_classifier = 0x10001;
SECTIONS { .vectors 0 : { KEEP(*(.vectors)) } .text 0x1000 : { *(.text*) *(.rodata*) } .stock 0x10000 : { KEEP(*(.stock)) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }
