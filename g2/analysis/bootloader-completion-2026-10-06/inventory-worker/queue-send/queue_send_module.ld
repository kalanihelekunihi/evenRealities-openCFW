ENTRY(opencfw_bl_kernel_queue_put_blocking)
opencfw_boot_timeout_capture = 0x418913;
opencfw_boot_timeout_check = 0x418923;
opencfw_boot_wait_list_sorted = 0x41863f;
opencfw_boot_timer_queue_unlock = 0x41a557;
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_bl_kernel_enter = 0x41b3e5;
opencfw_bl_kernel_exit = 0x41b3fd;
opencfw_bl_scheduler_suspend = 0x4181d9;
opencfw_bl_scheduler_resume = 0x418229;
opencfw_bl_kernel_reschedule = 0x41b3d1;
opencfw_bl_queue_runtime_mode = 0x418b57;
opencfw_bl_remove_event_waiter = 0x41872d;
opencfw_boot_queue_buffer_release = 0x418c1f;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
