ENTRY(case_binary_forward_candidate)
case_binary_forward_control = 0x0010f001;
case_binary_forward_dispatch = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
