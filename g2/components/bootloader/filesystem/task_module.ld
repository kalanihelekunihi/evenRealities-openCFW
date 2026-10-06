ENTRY(opencfw_boot_verify)
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } .boot_modes 0x0042dad0 : { *(.boot_modes) } .boot_path 0x004336e4 : { *(.boot_path) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_fs_mutex_acquire = 0x4166ab;
opencfw_boot_fs_mutex_release = 0x416711;
opencfw_boot_nor_read = 0x420f71;
opencfw_boot_nor_prog = 0x420b0d;
opencfw_boot_nor_erase = 0x420a09;
opencfw_boot_fs_error = 0x415faf;
opencfw_boot_runtime_call = 0x41e349;
opencfw_boot_log = 0x4176cf;
opencfw_boot_allocator_log = 0x08002101;
printf = 0x08002111;
opencfw_boot_dfu_queue_get = 0x416921;
opencfw_boot_dfu_runtime_enable = 0x42ddf3;
opencfw_boot_dfu_error_transaction = 0x42de0f;
opencfw_boot_dfu_log = 0x08002121;
