ENTRY(opencfw_spot_pcm22_transition15)
SECTIONS
{
  . = 0x3f500;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
