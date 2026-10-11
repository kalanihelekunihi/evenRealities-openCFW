case_tick_word2 = 0x0010f001;
case_flash_erase_mode4 = 0x0010f101;
case_flash_erase_page = 0x0010f201;
case_flash_program_doubleword = 0x0010f301;
case_flash_copy_operation = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
