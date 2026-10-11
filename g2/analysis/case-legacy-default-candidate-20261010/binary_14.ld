ENTRY(case_binary_14_candidate)
case_binary_14_read_a = 0x0010f001;
case_binary_14_scale = 0x0010f101;
case_binary_14_read_b = 0x0010f201;
case_binary_14_read_c = 0x0010f301;
case_binary_14_send = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
