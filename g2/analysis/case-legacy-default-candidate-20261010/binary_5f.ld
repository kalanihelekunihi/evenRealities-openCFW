ENTRY(case_binary_5f_candidate)
case_binary_fill5f = 0x0010f001;
case_binary_send5f = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
