ENTRY(opencfw_provider_4240aa)
opencfw_bl_critical_save = 0x0041b8ed;
opencfw_hal_delay_us = 0x0041d1c1;
opencfw_bl_clock_request = 0x004222f1;
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
