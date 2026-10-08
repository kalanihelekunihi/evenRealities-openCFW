ENTRY(opencfw_provider_420890)
SECTIONS
{
  . = 0x00012100;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
PROVIDE(opencfw_provider_4205f4 = 0x00013001);
PROVIDE(opencfw_provider_42069e = 0x00013021);
PROVIDE(opencfw_provider_420984 = 0x00013041);
PROVIDE(opencfw_provider_4209c4 = 0x00013061);
PROVIDE(opencfw_bl_nor_read_delay = 0x00013081);
PROVIDE(opencfw_bl_log = 0x000130a1);
