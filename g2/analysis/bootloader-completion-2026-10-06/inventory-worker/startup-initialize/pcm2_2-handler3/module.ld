ENTRY(opencfw_spot_pcm22_transition3)
SECTIONS
{
  . = 0x3fd00;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
