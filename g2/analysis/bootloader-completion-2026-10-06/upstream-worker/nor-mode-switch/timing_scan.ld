ENTRY(opencfw_provider_420002)
SECTIONS
{
  . = 0x00014100;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
PROVIDE(opencfw_hal_mspi_control = 0x0001f001);
PROVIDE(opencfw_bl_mspi_status_transfer = 0x0001f021);
PROVIDE(opencfw_bl_log = 0x0001f041);
PROVIDE(opencfw_provider_4176ce = opencfw_bl_log);
