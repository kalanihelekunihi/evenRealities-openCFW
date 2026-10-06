ENTRY(opencfw_hal_mspi_device_configure)
PROVIDE(opencfw_hal_delay_us = 0x08000100);
PROVIDE(clock_request = 0x08000120);
PROVIDE(clock_release = 0x08000140);
SECTIONS
{
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
