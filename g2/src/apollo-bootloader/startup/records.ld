ENTRY(opencfw_boot_init_records_run)
opencfw_boot_platform_system_init = 0x41b863;
opencfw_boot_platform_terminal = 0x4329c5;
SECTIONS {
 . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) }
 . = 0x415326; .boot_expand_adapter : { *(.boot_expand_adapter) }
 . = 0x431e38; .boot_zero_adapter : { *(.boot_zero_adapter) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
