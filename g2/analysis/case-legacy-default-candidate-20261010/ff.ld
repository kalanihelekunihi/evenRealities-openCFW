ENTRY(case_legacy_ff_prefix)
case_legacy_logger = 0x0010f201;
case_legacy_reset_first = 0x0010f001;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
