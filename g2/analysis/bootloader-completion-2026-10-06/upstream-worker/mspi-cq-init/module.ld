ENTRY(opencfw_bl_mspi_cq_init)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .cmdq_provider : { *(.cmdq_provider*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
