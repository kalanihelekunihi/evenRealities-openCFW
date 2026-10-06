ENTRY(opencfw_bl_kernel_queue_get_blocking)
opencfw_boot_kernel_queue_get_blocking = opencfw_bl_kernel_queue_get_blocking;
opencfw_boot_kernel_queue_create_dynamic = opencfw_bl_kernel_queue_create_dynamic;
opencfw_bl_rtos_allocate = 0x419731;
opencfw_bl_remove_event_waiter = 0x41872d;
opencfw_bl_missed_yield = 0x4189a3;
opencfw_bl_timer_expire = 0x419407;
opencfw_bl_timer_rollover = 0x41965d;
opencfw_bl_timer_process_commands = 0x419547;
opencfw_bl_tick_increment = 0x418409;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
