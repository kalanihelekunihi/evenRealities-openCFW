ENTRY(case_binary_3d_candidate)
case_binary_3d_control = 0x0010f001;
case_binary_3d_logger = 0x0010f101;
case_binary_3d_dispatch = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
