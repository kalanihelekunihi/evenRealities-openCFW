/* Bounded source oracle placement for reconstructed scatter records and data. */
ENTRY(opencfw_boot_init_records_run)
PHDRS {
 text PT_LOAD FLAGS(5);
 expand PT_LOAD FLAGS(5);
 zero PT_LOAD FLAGS(5);
 records PT_LOAD FLAGS(4);
 config PT_LOAD FLAGS(4);
 platform PT_LOAD FLAGS(4);
 color PT_LOAD FLAGS(4);
 level PT_LOAD FLAGS(4);
}
SECTIONS {
 . = 0x10000; .text : { *(.text*) *(.rodata*) } :text
 . = 0x415326; .boot_expand_adapter : { *(.boot_expand_adapter) } :expand
 . = 0x431e38; .boot_zero_adapter : { *(.boot_zero_adapter) } :zero
 . = 0x4330d8; .boot_init_records : { KEEP(*(.boot_init_records)) } :records
 . = 0x433d58; .boot_context_config : { KEEP(*(.boot_context_config)) } :config
 . = 0x433d98; .boot_platform_config : { KEEP(*(.boot_platform_config)) } :platform
 . = 0x43403c; .boot_elog_color_suffixes : { KEEP(*(.boot_elog_color_suffixes)) } :color
 . = 0x434178; .boot_elog_level_suffixes : { KEEP(*(.boot_elog_level_suffixes)) } :level
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
