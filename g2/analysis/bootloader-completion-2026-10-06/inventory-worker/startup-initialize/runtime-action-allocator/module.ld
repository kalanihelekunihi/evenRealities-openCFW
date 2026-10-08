ENTRY(opencfw_boot_thread_release_storage)
PROVIDE(opencfw_bl_scheduler_suspend = 0x08001001);
PROVIDE(opencfw_bl_scheduler_resume = 0x08001021);
PROVIDE(opencfw_bl_malloc_failed = 0x08001041);
PROVIDE(opencfw_bl_mask_interrupts = 0x08001061);
SECTIONS {
  . = 0x10000;
  .text : {
    KEEP(*(.text.opencfw_boot_thread_release_storage))
    KEEP(*(.text.opencfw_bl_rtos_allocate))
    KEEP(*(.text.opencfw_boot_rtos_heap_initialize))
    *(.text*) *(.rodata*)
  }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
