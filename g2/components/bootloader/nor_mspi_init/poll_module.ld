ENTRY(opencfw_hal_status_poll)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_hal_delay_us = 0x41d1c1;
