ENTRY(case_legacy_b0_branch)
case_legacy_b0_child = 0x0010fc01;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
