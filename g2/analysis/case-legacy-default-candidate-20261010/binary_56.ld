ENTRY(case_binary_56_candidate)
case_binary_56_logger = 0x0010f001;
case_binary_56_exit = 0x0010f101;
case_binary_56_ack = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
