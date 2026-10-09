ENTRY(Cy_SCB_ReadArray)
SECTIONS {
 .read_helper 0x9218 : { *(.text.Cy_SCB_ReadArrayNoCheck) }
 .read 0x9250 : { *(.text.Cy_SCB_ReadArray) }
 .write_helper 0x926e : { *(.text.Cy_SCB_WriteArrayNoCheck) }
 .write 0x92a6 : { *(.text.Cy_SCB_WriteArray) }
 .default_helper 0x92d6 : { *(.text.Cy_SCB_WriteDefaultArrayNoCheck) }
 .default 0x92e6 : { *(.text.Cy_SCB_WriteDefaultArray) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
