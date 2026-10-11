ENTRY(case_binary_guarded_sensor_read)
case_binary_sensor_transaction = 0x0010f001;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
