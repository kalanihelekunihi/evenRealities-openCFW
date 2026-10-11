ENTRY(opencfw_bl_instance_configure)
opencfw_boot_iom_clock_config = 0x42c26b;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
