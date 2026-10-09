ENTRY(Cy_SysTick_Init)
EXTERN(Cy_SysTick_SetCallback)
__RAM_VECTOR_TABLE = 0x20000400;
SECTIONS {
 .service 0xA5F4 : { *(.text.Cy_SysTick_ServiceCallbacks) }
 .enable 0xA620 : { *(.text.Cy_SysTick_Enable) }
 .clock 0xA638 : { *(.text.Cy_SysTick_SetClockSource) }
 .init 0xA650 : { *(.text.Cy_SysTick_Init) }
 .set_callback 0xA6A8 : { *(.text.Cy_SysTick_SetCallback) }
 .callbacks 0x20000F40 (NOLOAD) : { *(.bss) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
