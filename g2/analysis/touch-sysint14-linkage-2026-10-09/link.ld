ENTRY(Cy_SysInt_Init)
__RAM_VECTOR_TABLE = 0x20000400;
__Vectors = 0x3300;
SECTIONS {
 .nvic 0xA214 : { *(.text.__NVIC_SetPriority) }
 .vector 0xA274 : { *(.text.Cy_SysInt_SetVector) }
 .init 0xA2A8 : { *(.text.Cy_SysInt_Init) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
