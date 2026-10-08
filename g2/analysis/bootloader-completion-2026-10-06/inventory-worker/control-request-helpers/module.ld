ENTRY(opencfw_boot_mode_flags)
opencfw_boot_mode_flags = opencfw_bl_control_stage_two_flags;
opencfw_boot_queue_post = opencfw_provider_427c12;
opencfw_boot_queue_release = opencfw_provider_4279be;
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
