ENTRY(opencfw_boot_dfu_thread_deinit_native)
opencfw_boot_dfu_thread_terminate = 0x08000101;
opencfw_provider_416200 = 0x08000111;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
