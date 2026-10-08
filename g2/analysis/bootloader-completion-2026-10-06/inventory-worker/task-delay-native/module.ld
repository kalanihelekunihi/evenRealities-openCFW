ENTRY(opencfw_cmsis_delay)
SECTIONS{.text 0x70000 : {*(.text*) *(.rodata*)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}
opencfw_bl_context_guard = 0x08000101;
opencfw_bl_mask_interrupts = 0x08000111;
opencfw_bl_scheduler_suspend = 0x08000121;
opencfw_boot_task_block = 0x08000131;
opencfw_bl_scheduler_resume = 0x08000141;
opencfw_bl_kernel_reschedule = 0x08000151;
