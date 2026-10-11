case_kernel_list_remove = 0x0010f001;
case_kernel_list_insert_tail = 0x0010f101;
case_kernel_list_insert_ordered = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
