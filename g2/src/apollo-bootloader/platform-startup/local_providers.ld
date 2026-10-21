ENTRY(opencfw_boot_coprocessor_enable)
opencfw_boot_control_critical_save = 0x08000101;
opencfw_hal_delay_us = 0x08000121;
SECTIONS { . = 0x10000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }
