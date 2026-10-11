ENTRY(case_binary_56_exit)
case_binary_56_cancel = 0x0010f001;
case_binary_56_clear_a = 0x0010f101;
case_binary_56_clear_b = 0x0010f201;
case_binary_56_exit_log = 0x0010f301;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
