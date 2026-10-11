ENTRY(opencfw_bl_stack_overflow)
opencfw_boot_plain_printf = 0x08000101;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
