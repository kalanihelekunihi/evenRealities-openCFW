ENTRY(opencfw_boot_thread_new)
opencfw_bl_malloc_failed = 0x41b5f7;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
