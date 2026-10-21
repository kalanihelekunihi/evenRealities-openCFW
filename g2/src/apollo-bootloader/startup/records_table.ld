ENTRY(opencfw_boot_init_records_run)
PHDRS {
 text PT_LOAD FLAGS(5);
 expand PT_LOAD FLAGS(5);
 zero PT_LOAD FLAGS(5);
 records PT_LOAD FLAGS(4);
}
opencfw_boot_platform_system_init = 0x41b863;
opencfw_boot_platform_terminal = 0x4329c5;
SECTIONS {
 . = 0x10000; .text : { *(.text*) *(.rodata*) } :text
 . = 0x415326; .boot_expand_adapter : { *(.boot_expand_adapter) } :expand
 . = 0x431e38; .boot_zero_adapter : { *(.boot_zero_adapter) } :zero
 . = 0x4330d8; .boot_init_records : { KEEP(*(.boot_init_records)) } :records
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
