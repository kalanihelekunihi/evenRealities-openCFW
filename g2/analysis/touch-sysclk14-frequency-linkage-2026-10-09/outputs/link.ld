ENTRY(Cy_SysClk_ImoSetFrequency)
EXTERN(Cy_SysClk_ClkHfGetFrequency)
__aeabi_uidiv = 0xA6C1;
SECTIONS {
 .assembly 0x4480 : { *assembly.o(.text) }
 .external 0x9C38 : { *(.text.Cy_SysClk_ExtClkGetFrequency) }
 .imo_get 0x9C44 : { *(.text.Cy_SysClk_ImoGetFrequency) }
 .imo_set 0x9C80 : { *(.text.Cy_SysClk_ImoSetFrequency) }
 .source_get 0x9F34 : { *(.text.Cy_SysClk_ClkHfGetSource) }
 .frequency 0x9F9C : { *(.text.Cy_SysClk_ClkHfGetFrequency) }
 .globals 0x20000F20 (NOLOAD) : { *(.bss) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
