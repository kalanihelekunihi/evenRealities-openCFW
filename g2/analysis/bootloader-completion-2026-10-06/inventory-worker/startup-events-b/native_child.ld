ENTRY(native_spot_temperature_range)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } . = ALIGN(4); .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } }
