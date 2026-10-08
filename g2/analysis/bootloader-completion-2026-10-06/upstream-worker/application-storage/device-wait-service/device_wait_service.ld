ENTRY(opencfw_boot_device_wait_service)
PROVIDE(opencfw_boot_rom48 = 0x080002a1);
SECTIONS
{
  . = 0x432000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
