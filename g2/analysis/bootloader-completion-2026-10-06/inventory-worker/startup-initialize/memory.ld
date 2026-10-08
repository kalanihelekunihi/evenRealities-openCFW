opencfw_hal_status_poll = 0x08000201;
opencfw_boot_power_callback = 0x08000211;
ENTRY(opencfw_boot_startup_mcu_memory)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
