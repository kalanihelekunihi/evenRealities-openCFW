ENTRY(reset_entry)
SECTIONS {
 .vectors 0 : { KEEP(*(.vectors)) }
 .text 0x1000 : { *(.text*) *(.rodata*) }
 .data 0x20040000 : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) }
}
