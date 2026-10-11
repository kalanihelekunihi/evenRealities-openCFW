ENTRY(case_binary_51_candidate)
case_binary_fill51 = 0x0010f001;
case_binary_send51 = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
