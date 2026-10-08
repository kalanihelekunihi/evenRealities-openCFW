ENTRY(opencfw_boot_manager_thread_deinit)
SECTIONS {
 . = 0x38000;
 .text : { *(.text.opencfw_boot_manager_thread_deinit) *(.text.opencfw_boot_dfu_thread_deinit) }
 .text.other : { *(.text .text.*) }
}
