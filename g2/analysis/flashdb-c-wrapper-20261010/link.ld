ENTRY(g2_flashdb_candidate_blob_read)
SECTIONS { . = 0x100000; .text : { *(.text*) } .rodata : { *(.rodata*) } . = 0x20090000; .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } }
