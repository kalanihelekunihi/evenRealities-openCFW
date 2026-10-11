ENTRY(case_legacy_ee_prefix)
case_legacy_logger = 0x0010f201;
case_legacy_ee_first = 0x0010ff01;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
