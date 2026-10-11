case_bus_prepare = 0x0010f001;
case_bus_finish = 0x0010f101;
case_bus_send = 0x0010f201;
case_bus_start = 0x0010f301;
case_bus_poll = 0x0010f401;
case_bus_read = 0x0010f501;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
