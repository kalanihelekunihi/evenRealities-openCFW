ENTRY(opencfw_bl_nor_read_before)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

opencfw_bl_copy = 0x004156ad;
opencfw_bl_power_control = 0x00426809;
opencfw_bl_check_activity = 0x004166ab;
opencfw_bl_check_pending = 0x00416711;
opencfw_bl_log = 0x004176cf;
opencfw_bl_delay = 0x0041d1c1;
opencfw_bl_runtime_mode = 0x00418b57;
opencfw_bl_notify = 0x00416379;
opencfw_bl_poll_status = 0x004205f5;
opencfw_bl_mspi_disable = 0x004250f1;
opencfw_bl_mspi_device_configure = 0x00424be5;
opencfw_bl_mspi_enable = 0x00425067;
opencfw_bl_mspi_control = 0x004251c1;
opencfw_bl_publish_device_state = 0x0041fadd;
