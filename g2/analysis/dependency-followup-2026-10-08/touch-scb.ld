ENTRY(Cy_SCB_ReadArray)
SECTIONS {
 .text 0x9218 : { *(.text.Cy_SCB_ReadArrayNoCheck) *(.text.Cy_SCB_ReadArray) *(.text.Cy_SCB_WriteArrayNoCheck) *(.text.Cy_SCB_WriteArray) *(.text.Cy_SCB_WriteDefaultArrayNoCheck) *(.text.Cy_SCB_WriteDefaultArray) }
 /DISCARD/ : { *(.text*) *(.data*) *(.bss*) *(.ARM.exidx*) *(.ARM.extab*) }
}
ASSERT(SIZEOF(.text) == 254, "selected SCB source extents changed")
