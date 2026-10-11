ENTRY(case_binary_sensor_start)
case_binary_sensor_line_a = 0x0010f001;
case_binary_sensor_line_b = 0x0010f101;
case_binary_sensor_delay = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
