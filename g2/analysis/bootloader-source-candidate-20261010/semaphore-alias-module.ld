ENTRY(opencfw_bl_semaphore_create)
opencfw_bl_context_guard = 0x41602b;
opencfw_bl_kernel_queue_create_dynamic = 0x419d09;
opencfw_bl_kernel_queue_create_static = 0x419c9d;
opencfw_bl_kernel_queue_put_blocking = 0x419ec1;
opencfw_bl_rtos_free = 0x419831;
opencfw_bl_mask_interrupts = 0x41b2f9;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
