ENTRY(probe_stop)
SECTIONS { .vectors 0 : {KEEP(*(.vectors))} .reset 0x1000 : {*(.reset)} .text 0x28000000 : {*(.text*) *(.rodata*)} .native_main 0x28100000 : {KEEP(*(.native_main))} /DISCARD/ : {*(.ARM.exidx*) *(.comment*)} }
