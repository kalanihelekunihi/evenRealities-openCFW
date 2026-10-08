ENTRY(state_event_dispatch_42d562_native)
opencfw_boot_rom_delay_cycles = 0x00000041;
SECTIONS
{
  . = 0x30000;
  .text : { *(.text*) *(.rodata*) }
  . = ALIGN(4);
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
