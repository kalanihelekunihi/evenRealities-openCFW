ENTRY(opencfw_bl_rtos_allocate)
opencfw_bl_scheduler_suspend = 0x4181d9;
opencfw_bl_scheduler_resume = 0x418229;
opencfw_bl_malloc_failed = 0x41b5f7;
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_boot_rtos_allocate = opencfw_bl_rtos_allocate;
opencfw_boot_rtos_free = opencfw_bl_rtos_free;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
