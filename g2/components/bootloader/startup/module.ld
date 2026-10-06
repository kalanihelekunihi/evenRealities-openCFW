ENTRY(opencfw_boot_expand_record)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
