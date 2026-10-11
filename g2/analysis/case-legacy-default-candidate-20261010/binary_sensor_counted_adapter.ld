ENTRY(case_binary_sensor_read_adapter)
case_binary_guarded_sensor_read = 0x0010f001;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
