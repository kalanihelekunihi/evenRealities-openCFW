ENTRY(opencfw_dfu_log_detail_native)
SECTIONS { . = 0x70000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
opencfw_boot_elog_output = 0x08000101;
