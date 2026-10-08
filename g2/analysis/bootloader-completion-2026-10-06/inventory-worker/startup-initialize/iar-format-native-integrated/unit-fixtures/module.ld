ENTRY(reset_entry)
SECTIONS{.vectors 0 : {KEEP(*(.vectors))}.text 0x1000 : {*(.text*) *(.rodata*)}.stock 0x40000 : {KEEP(*(.stock))}. = 0x20010000;.data : {*(.data*)}.bss : {*(.bss*) *(COMMON)} /DISCARD/ : {*(.ARM.exidx*) *(.ARM.extab*)}}
