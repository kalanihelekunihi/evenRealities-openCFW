case_control_write = 0x0010f001;
case_bus_gpio_config = 0x0010f101;
case_bus_positive_sample = 0x0010f201;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
