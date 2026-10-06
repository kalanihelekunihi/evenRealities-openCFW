ENTRY(opencfw_boot_control_mode_one)
EXTERN(opencfw_boot_control_mode_two opencfw_boot_control_cleanup opencfw_boot_control_power_apply opencfw_boot_control_transition opencfw_boot_control_query_descriptor_copy)
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
