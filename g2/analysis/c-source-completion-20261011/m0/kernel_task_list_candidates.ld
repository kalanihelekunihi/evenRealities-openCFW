case_kernel_invariant_failure = 0x0010f001;
case_kernel_list_insert_tail = 0x0010f101;
case_kernel_list_remove = 0x0010f201;
case_kernel_list_insert_ordered = 0x0010f301;
case_kernel_task_delay = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
