ENTRY(opencfw_boot_thread_new)
opencfw_bl_rtos_allocate = 0x419731;
opencfw_bl_rtos_free = 0x419831;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
