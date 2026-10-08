ENTRY(opencfw_cmsis_delay)
SECTIONS{.text 0x70000 : {*(.text*) *(.rodata*)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}
opencfw_bl_context_guard = 0x105f5;
opencfw_bl_mask_interrupts = 0x1062d;
opencfw_bl_scheduler_suspend = 0x15965;
opencfw_boot_task_block = 0x161bd;
opencfw_bl_scheduler_resume = 0x15991;
opencfw_bl_kernel_reschedule = 0x106cd;
