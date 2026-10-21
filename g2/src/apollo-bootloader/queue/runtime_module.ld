ENTRY(opencfw_bl_queue_create)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

/* Exact original BL destinations, encoded Thumb for C call relocations. */
/* runtime state query is source-defined */
opencfw_bl_kernel_queue_create_static = 0x00419c9d;
opencfw_bl_kernel_queue_create_dynamic = 0x00419d09;
opencfw_bl_kernel_queue_put_blocking = 0x00419ec1;
opencfw_bl_kernel_queue_put_from_isr = 0x0041a025;
opencfw_bl_kernel_queue_get_blocking = 0x0041a115;
opencfw_bl_kernel_queue_get_from_isr = 0x0041a3b1;
