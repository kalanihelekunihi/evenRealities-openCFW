ENTRY(case_binary_3f_candidate)
case_binary_3f_logger = 0x0010f001;
case_binary_3f_enable = 0x0010f101;
case_binary_3f_ack = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
