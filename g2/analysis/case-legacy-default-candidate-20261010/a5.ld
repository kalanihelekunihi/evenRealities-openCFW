ENTRY(case_legacy_a5_branch)
case_legacy_logger = 0x0010f201;
case_legacy_hex_log = 0x0010f401;
case_legacy_set_sn = 0x0010f801;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
