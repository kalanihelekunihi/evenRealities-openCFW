ENTRY(opencfw_boot_context_interrupt_enable)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
