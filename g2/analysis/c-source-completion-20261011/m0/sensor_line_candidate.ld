case_control_write = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
