ENTRY(opencfw_task_return_native)
SECTIONS{.text 0x70000 : {*(.text*) *(.rodata*)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}
opencfw_boot_manager_start_signal = 0x08000101;
opencfw_cmsis_delay = 0x08000111;
opencfw_boot_plain_printf = 0x08000121;
opencfw_bl_mask_interrupts = 0x08000131;
opencfw_iar_exit = 0x08000141;
