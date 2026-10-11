ENTRY(case_binary_local_four_candidate)
case_binary_local_send = 0x0010f001;
case_binary_local_ack = 0x0010f101;
case_binary_local_control_a = 0x0010f201;
case_binary_local_control_b = 0x0010f301;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
