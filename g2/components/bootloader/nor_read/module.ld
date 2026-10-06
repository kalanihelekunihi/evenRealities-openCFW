ENTRY(opencfw_boot_nor_read)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

/* Stock BL call targets, Thumb aliases. */
opencfw_bl_nor_read_before = 0x0041ff09;
opencfw_bl_nor_read_configure = 0x00420e8d;
opencfw_bl_nor_read_delay = 0x004207f5;
opencfw_bl_nor_read_after = 0x0041ff1f;
opencfw_bl_mspi_blocking_transfer = 0x004262e1;
