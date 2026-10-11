ENTRY(opencfw_bl_config_transaction)
opencfw_bl_mspi_mode_enter = 0x41bf85;
opencfw_bl_mspi_mode_leave = 0x41c17b;
clock_request = 0x4222f1;
clock_release = 0x422365;
opencfw_boot_iom_cq_enable = 0x42c421;
opencfw_boot_iom_cq_disable = 0x42c44f;
opencfw_hal_status_poll = 0x41d247;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
