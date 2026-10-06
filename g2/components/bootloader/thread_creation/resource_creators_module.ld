ENTRY(opencfw_provider_4163b2)
opencfw_boot_timer_new = opencfw_provider_4163b2;
opencfw_boot_mutex_new = opencfw_provider_416610;
opencfw_bl_context_guard = 0x41602b;
opencfw_bl_kernel_enter = 0x41b3e5;
opencfw_bl_kernel_exit = 0x41b3fd;
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_bl_rtos_allocate = 0x419731;
opencfw_bl_rtos_free = 0x419831;
opencfw_boot_timer_initialize = 0x419685;
opencfw_bl_kernel_queue_create_dynamic = 0x419d09;
opencfw_boot_timer_queue_fresh = 0x419c9d;
opencfw_bl_kernel_queue_put_blocking = 0x419ec1;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
