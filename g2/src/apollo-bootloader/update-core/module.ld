ENTRY(opencfw_boot_verify)
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } .boot_modes 0x0042dad0 : { *(.boot_modes) } .boot_path 0x004336e4 : { *(.boot_path) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_file_open = 0x4153a5;
opencfw_boot_file_prepare = 0x4154d3;
opencfw_boot_file_read = 0x415485;
opencfw_boot_file_close = 0x415447;
opencfw_boot_runtime_call = 0x41e349;
opencfw_boot_log = 0x4176cf;
