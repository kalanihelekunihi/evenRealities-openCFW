ENTRY(opencfw_boot_pendsv_entry)
opencfw_bl_stack_overflow = 0x41b601;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
