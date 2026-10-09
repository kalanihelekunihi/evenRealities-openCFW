ENTRY(Cy_SysClk_ClkHfSetSource)
SECTIONS {
 .external 0x9C38 : { *(.text.Cy_SysClk_ExtClkGetFrequency) }
 .get_source 0x9F34 : { *(.text.Cy_SysClk_ClkHfGetSource) }
 .set_source 0x9F44 : { *(.text.Cy_SysClk_ClkHfSetSource) }
 .globals 0x20000F20 (NOLOAD) : { *(.bss) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
