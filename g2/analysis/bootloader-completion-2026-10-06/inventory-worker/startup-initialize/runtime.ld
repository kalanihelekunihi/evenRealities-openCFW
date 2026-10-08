opencfw_boot_device_mode_wait = 0x08000201;
ENTRY(opencfw_boot_startup_spot_dispatch)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
