ENTRY(case_binary_5e_candidate)
case_binary_5e_apply = 0x0010f001;
case_binary_5e_ack = 0x0010f101;
case_binary_5e_send = 0x0010f201;
case_binary_5e_logger = 0x0010f301;
case_binary_5e_hex = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
