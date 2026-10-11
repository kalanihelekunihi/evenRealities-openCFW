ENTRY(opencfw_bl_context_enable)
opencfw_boot_iom_cq_initialize = 0x42c3e3;
opencfw_hal_status_poll = 0x41d247;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
