ENTRY(opencfw_bl_task_return)
opencfw_bl_mask_interrupts = 0x08000101;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
