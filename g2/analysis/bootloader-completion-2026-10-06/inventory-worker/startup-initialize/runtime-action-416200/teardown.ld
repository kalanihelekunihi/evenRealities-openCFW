ENTRY(opencfw_boot_runtime_action)
SECTIONS {
 . = 0x38000;
 .text : {
 KEEP(*runtime_action.o(.text .text.*))
 KEEP(*teardown.o(.text .text.*))
 KEEP(*dfu_context.o(.text.opencfw_boot_dfu_thread_deinit))
 KEEP(*teardown_native_aliases.o(.text .text.*))
 *(.text .text.*)
 }
 .rodata : { *(.rodata .rodata.*) }
}
