ENTRY(opencfw_provider_420c5c)
SECTIONS
{
  . = 0x00010100;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
PROVIDE(opencfw_provider_4205f4 = 0x00011001);
PROVIDE(opencfw_provider_42069e = 0x00011021);
PROVIDE(opencfw_provider_420984 = 0x00011041);
PROVIDE(opencfw_bl_nor_read_delay = 0x00011061);
PROVIDE(opencfw_bl_log = 0x00011081);
