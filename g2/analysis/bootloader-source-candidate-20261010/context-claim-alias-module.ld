ENTRY(opencfw_bl_context_claim)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
.bss.boot_iom_context_pool 0x2001455c (NOLOAD) : { *(.bss.boot_iom_context_pool) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
