ENTRY(opencfw_boot_dfu_terminal)
opencfw_boot_manager_start_signal = 0x08000101;
opencfw_cmsis_delay = 0x08000111;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
