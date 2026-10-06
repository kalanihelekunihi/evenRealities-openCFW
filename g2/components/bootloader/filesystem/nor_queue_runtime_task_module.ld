ENTRY(opencfw_boot_verify)
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } .boot_modes 0x0042dad0 : { *(.boot_modes) } .boot_path 0x004336e4 : { *(.boot_path) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_fs_mutex_acquire = 0x4166ab;
opencfw_boot_fs_mutex_release = 0x416711;
/* NOR read is source-defined */
opencfw_boot_nor_prog = 0x420b0d;
opencfw_boot_nor_erase = 0x420a09;
opencfw_boot_fs_error = 0x415faf;
opencfw_boot_runtime_call = 0x41e349;
opencfw_boot_log = 0x4176cf;
opencfw_boot_allocator_log = 0x08002101;
printf = 0x08002111;
opencfw_boot_dfu_queue_get = opencfw_bl_queue_get;
opencfw_boot_dfu_runtime_enable = 0x42ddf3;
opencfw_boot_dfu_error_transaction = 0x42de0f;
opencfw_boot_dfu_log = 0x08002121;

/* Exact original BL destinations, encoded Thumb for C call relocations. */
/* runtime query is source-defined */
opencfw_bl_kernel_queue_create_static = 0x00419c9d;
opencfw_bl_kernel_queue_create_dynamic = 0x00419d09;
opencfw_bl_kernel_queue_put_blocking = 0x00419ec1;
opencfw_bl_kernel_queue_put_from_isr = 0x0041a025;
opencfw_bl_kernel_queue_get_blocking = 0x0041a115;
opencfw_bl_kernel_queue_get_from_isr = 0x0041a3b1;

/* Stock BL call targets, Thumb aliases. */
opencfw_bl_nor_read_before = 0x0041ff09;
opencfw_bl_nor_read_configure = 0x00420e8d;
opencfw_bl_nor_read_delay = 0x004207f5;
opencfw_bl_nor_read_after = 0x0041ff1f;
opencfw_bl_mspi_blocking_transfer = 0x004262e1;
