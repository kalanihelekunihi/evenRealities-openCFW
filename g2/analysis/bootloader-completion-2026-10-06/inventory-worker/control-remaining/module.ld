ENTRY(opencfw_boot_control)
opencfw_boot_control = opencfw_hal_mspi_control;
opencfw_boot_mixed = opencfw_hal_mspi_pio_mixed;
opencfw_hal_delay_us = 0x0041d1c1;
opencfw_bl_delay_us = 0x0041d1c1;
opencfw_hal_mspi_control_unrecovered_request = opencfw_hal_mspi_control_queue_request;
opencfw_bl_critical_save = opencfw_boot_control_critical_save;
opencfw_bl_clock_request = 0x004222f1;
clock_release = 0x00422365;
clock_request = 0x004222f1;
clock_release = 0x00422365;
PHDRS { text PT_LOAD FLAGS(5); }
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  .data : { *(.data*) } :text
  .bss : { *(.bss*) *(COMMON) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
