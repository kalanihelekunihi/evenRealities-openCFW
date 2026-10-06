ENTRY(opencfw_bl_mspi_status_transfer)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

opencfw_bl_mspi_blocking_transfer = 0x004262e1;
opencfw_bl_status_transfer_error = 0x00415faf;
