ENTRY(case_legacy_a1_branch)
case_legacy_gpio_bit4 = 0x0010f001;
case_legacy_gpio_bit0 = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
