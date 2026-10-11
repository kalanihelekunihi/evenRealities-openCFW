case_bus_drive_a = 0x0010f001;
case_bus_drive_b = 0x0010f101;
case_bus_drive_c = 0x0010f201;
case_bus_delay = 0x0010f301;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
