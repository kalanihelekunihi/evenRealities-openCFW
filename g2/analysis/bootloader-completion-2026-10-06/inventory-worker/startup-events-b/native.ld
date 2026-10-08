ENTRY(opencfw_boot_spot_state_power_event)
SECTIONS
{
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  . = ALIGN(4);
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
