ENTRY(case_legacy_a2_branch)
case_legacy_fill8 = 0x0010f301;
case_legacy_hex_log = 0x0010f401;
case_legacy_logger = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
