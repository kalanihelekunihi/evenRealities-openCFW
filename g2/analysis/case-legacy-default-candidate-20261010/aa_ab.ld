ENTRY(case_legacy_aa_branch)
case_legacy_aa_first = 0x0010f901;
case_legacy_aa_second = 0x0010fa01;
case_legacy_ab_child = 0x0010fb01;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
