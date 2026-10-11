ENTRY(case_legacy_a3_branch)
case_legacy_value_a = 0x0010f501;
case_legacy_value_b = 0x0010f601;
case_legacy_value_c = 0x0010f701;
case_legacy_logger = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
