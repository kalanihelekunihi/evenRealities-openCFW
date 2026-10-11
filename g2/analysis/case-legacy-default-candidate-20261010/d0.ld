ENTRY(case_legacy_d0_branch)
case_legacy_watchdog_set = 0x0010fe01;
case_legacy_logger = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
