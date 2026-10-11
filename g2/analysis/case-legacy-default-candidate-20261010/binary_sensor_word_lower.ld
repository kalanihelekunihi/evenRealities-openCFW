ENTRY(case_binary_read_word_lower)
case_binary_sensor_read_adapter = 0x0010f001;
case_binary_sensor_delay_count = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
