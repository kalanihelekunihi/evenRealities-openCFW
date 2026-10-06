ENTRY(opencfw_bl_mspi_enable)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .cq_provider : { *(.cq_provider*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
