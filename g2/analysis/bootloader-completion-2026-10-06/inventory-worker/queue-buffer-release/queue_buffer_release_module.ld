ENTRY(opencfw_boot_queue_buffer_release)
opencfw_boot_list_unlink = 0x41b5a9;
opencfw_bl_mask_interrupts = 0x41b2f9;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
