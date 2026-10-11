case_binary_5e_flash_mode = 0x0010f001;
case_binary_5e_flash_init = 0x0010f101;
case_binary_5e_flash_read = 0x0010f201;
case_binary_5e_wait = 0x0010f301;
case_binary_5e_flash_program = 0x0010f401;
case_binary_5e_flash_finish = 0x0010f501;
case_binary_5e_failure_log = 0x0010f601;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
