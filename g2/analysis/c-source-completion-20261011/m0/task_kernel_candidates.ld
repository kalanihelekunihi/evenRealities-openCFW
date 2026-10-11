case_kernel_enter = 0x0010f001;
case_kernel_exit = 0x0010f101;
case_kernel_mode = 0x0010f201;
case_kernel_queue_send = 0x0010f301;
case_kernel_queue_post = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
