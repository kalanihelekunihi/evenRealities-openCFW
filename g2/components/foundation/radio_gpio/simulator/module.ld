ENTRY(GPIO0_607F_IRQHandler)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } . = 0x20000000; .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } }
