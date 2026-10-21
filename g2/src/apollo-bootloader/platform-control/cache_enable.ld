ENTRY(opencfw_boot_icache_enable)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
