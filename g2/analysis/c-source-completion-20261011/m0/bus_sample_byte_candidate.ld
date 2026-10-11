case_bus_response_sample = 0x0010f001;
case_bus_read = 0x0010f101;
case_bus_start = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
