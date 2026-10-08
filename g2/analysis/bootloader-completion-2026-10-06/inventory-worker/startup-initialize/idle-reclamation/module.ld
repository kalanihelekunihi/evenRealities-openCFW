ENTRY(opencfw_boot_idle_cleanup)
SECTIONS { . = 0x50000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) } }
