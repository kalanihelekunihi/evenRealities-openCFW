ENTRY(opencfw_boot_first_task_restore)
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_boot_thread_select = 0x418571;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
