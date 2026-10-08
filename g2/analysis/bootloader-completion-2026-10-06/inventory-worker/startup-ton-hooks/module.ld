ENTRY(opencfw_ton_trim_cache)
PROVIDE(ton_cut_41c838 = 0x08000101);
PROVIDE(ton_cut_41d1c0 = 0x08000121);
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
