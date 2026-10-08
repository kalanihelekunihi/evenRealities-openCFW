ENTRY(opencfw_boot_storage_range_valid)
PROVIDE(opencfw_hal_delay_us = 0x08000200);
PROVIDE(opencfw_boot_device_info_configure = 0x08000240);
PROVIDE(opencfw_boot_device_wait_service = 0x08000280);
SECTIONS
{
  . = 0x432000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  . = 0x433754;
  .boot_device_clock_factors : { *(.boot_device_clock_factors) }
  . = 0x43401c;
  .boot_storage_range_table : { *(.boot_storage_range_table) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
