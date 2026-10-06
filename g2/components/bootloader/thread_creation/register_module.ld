ENTRY(opencfw_boot_thread_new)
opencfw_bl_context_guard = 0x41602b;
opencfw_bl_kernel_dynamic_thread = 0x417d17;
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_bl_kernel_enter = 0x41b3e5;
opencfw_bl_kernel_exit = 0x41b3fd;
opencfw_bl_ready_lists_initialize = 0x418a45;
opencfw_bl_kernel_reschedule = 0x41b3d1;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
