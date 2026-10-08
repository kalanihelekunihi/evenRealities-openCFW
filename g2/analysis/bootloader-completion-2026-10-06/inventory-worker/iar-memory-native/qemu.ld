ENTRY(Reset_Handler)
SECTIONS { . = 0; .vectors : { *(.vectors) } . = 0x1000; .text : { *(.text*) *(.rodata*) } . = 0x40000; .stock : { *(.stock) } . = 0x20010000; .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
