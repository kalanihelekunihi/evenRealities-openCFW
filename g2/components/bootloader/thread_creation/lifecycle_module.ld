ENTRY(opencfw_boot_kernel_initialize)
opencfw_bl_kernel_start = 0x418149;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
