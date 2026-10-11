ENTRY(opencfw_boot_power_control)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
