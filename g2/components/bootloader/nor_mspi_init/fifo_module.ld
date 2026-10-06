ENTRY(opencfw_hal_mspi_fifo_read)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_hal_status_poll = 0x41d247;
