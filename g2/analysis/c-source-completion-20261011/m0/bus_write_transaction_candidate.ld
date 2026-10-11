case_bus_output_finish = 0x0010f001;
case_bus_output_send = 0x0010f101;
case_bus_output_start = 0x0010f201;
case_bus_output_poll = 0x0010f301;
case_bus_read = 0x0010f401;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
