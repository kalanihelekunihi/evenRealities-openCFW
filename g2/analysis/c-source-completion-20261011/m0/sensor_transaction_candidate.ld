case_binary_sensor_start = 0x0010f001;
case_binary_sensor_byte_output = 0x0010f101;
case_binary_sensor_ack = 0x0010f201;
case_binary_sensor_byte_input = 0x0010f301;
case_binary_sensor_interbyte_pulse = 0x0010f401;
case_binary_sensor_final_pulse = 0x0010f501;
case_binary_sensor_stop = 0x0010f601;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
