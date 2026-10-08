ENTRY(opencfw_provider_42790a)
opencfw_bl_critical_save = 0x0041b8ed;
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
