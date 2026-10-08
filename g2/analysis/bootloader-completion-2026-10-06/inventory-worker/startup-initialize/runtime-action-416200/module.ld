ENTRY(opencfw_boot_runtime_action)
SECTIONS {
 . = 0x38000;
 .text : { KEEP(*(.text .text.*)) }
 .rodata : { *(.rodata .rodata.*) }
}
