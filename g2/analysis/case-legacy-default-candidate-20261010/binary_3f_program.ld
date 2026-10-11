ENTRY(case_binary_3f_program)
case_binary_3f_bus = 0x0010f001;
case_binary_3f_program_log = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
