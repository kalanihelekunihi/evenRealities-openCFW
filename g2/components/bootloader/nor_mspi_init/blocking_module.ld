ENTRY(opencfw_bl_mspi_blocking_transfer)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_hal_mspi_fifo_read = 0x423e8b;
opencfw_hal_mspi_fifo_write = 0x423e41;
opencfw_hal_status_poll = 0x41d247;
