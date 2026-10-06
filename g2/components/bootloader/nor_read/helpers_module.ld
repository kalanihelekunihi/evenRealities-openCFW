ENTRY(opencfw_bl_nor_read_before)
opencfw_boot_fs_mutex_acquire = 0x4166ab;
opencfw_boot_fs_mutex_release = 0x416711;
opencfw_provider_41fe28 = 0x41fe29;
opencfw_provider_41fe48 = 0x41fe49;
opencfw_provider_420e08 = 0x420e09;
opencfw_hal_mspi_control = 0x4251c1;
opencfw_bl_mspi_status_transfer = 0x4205f5;
opencfw_bl_delay_raw = 0x41f9e7;
opencfw_bl_kernel_state = 0x416089;
opencfw_bl_task_delay = 0x416379;
opencfw_bl_log = 0x4176cf;
SECTIONS { .  =  0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
