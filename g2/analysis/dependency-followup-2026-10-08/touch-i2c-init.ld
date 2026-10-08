ENTRY(Cy_SCB_I2C_Init)
SECTIONS { .text 0x100000 : { *(.text.Cy_SCB_I2C_Init) } /DISCARD/ : { *(.text*) *(.data*) *(.bss*) *(.ARM.exidx*) *(.ARM.extab*) } }
