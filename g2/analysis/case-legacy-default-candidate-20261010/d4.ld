ENTRY(case_legacy_d4_branch)
case_legacy_logger = 0x0010f201;
case_legacy_pmic_set = 0x0010fd01;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
