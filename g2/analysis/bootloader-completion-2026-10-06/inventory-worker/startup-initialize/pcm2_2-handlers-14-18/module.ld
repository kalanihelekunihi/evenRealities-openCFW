ENTRY(opencfw_spot_pcm22_transition14)
PROVIDE(opencfw_hal_delay_us = opencfw_bl_delay_us);
SECTIONS
{
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
