ENTRY(case_binary_14_read_a)
case_binary_read_byte_lower = 0x0010f001;
case_binary_read_word_lower = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
