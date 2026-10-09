ENTRY(Cy_GPIO_Pin_Init)
SECTIONS {
 .gpio_hsiom 0x8e28 : { *(.text.Cy_GPIO_SetHSIOM) }
 .gpio_write 0x8e64 : { *(.text.Cy_GPIO_Write) }
 .gpio_drive 0x8e84 : { *(.text.Cy_GPIO_SetDrivemode) }
 .gpio_edge 0x8ebe : { *(.text.Cy_GPIO_SetInterruptEdge) }
 .gpio_init 0x8ee4 : { *(.text.Cy_GPIO_Pin_Init) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
