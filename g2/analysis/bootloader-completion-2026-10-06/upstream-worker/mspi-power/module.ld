ENTRY(opencfw_bl_power_control)
/* Deterministic synthetic callouts for the isolated three-argument adapter
 * profile. The verifier intercepts these addresses; they are not firmware. */
PROVIDE(opencfw_bl_mspi_mode_enter = 0x08000100);
PROVIDE(opencfw_bl_mspi_mode_leave = 0x08000120);
PROVIDE(clock_request = 0x08000140);
PROVIDE(opencfw_bl_clock_release_all = 0x08000160);
PROVIDE(opencfw_bl_mspi_clockgen_control = 0x08000180);
PROVIDE(opencfw_hal_mspi_cq_disable = 0x080001a0);
PROVIDE(opencfw_bl_mspi_cq_enable = 0x080001c0);
PROVIDE(opencfw_hal_delay_us = 0x08000200);
SECTIONS
{
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
