ENTRY(opencfw_bl_mspi_mode_enter)
opencfw_boot_control_critical_save = 0x41b8ed;
opencfw_hal_status_poll = 0x41d247;
opencfw_boot_control_delay_status_change = 0x41d21d;
opencfw_hal_delay_us = 0x41d1c1;
opencfw_boot_power_special_mode = 0x41bae9;
opencfw_bl_clock_release_all = 0x4223d9;
clock_request = 0x4222f1;
clock_release = 0x422365;
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
