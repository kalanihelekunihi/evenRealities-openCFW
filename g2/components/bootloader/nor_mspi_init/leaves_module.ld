ENTRY(opencfw_hal_mspi_interrupt_clear)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_hal_mspi_cq_init = 0x423f29;
opencfw_hal_mspi_cq_disable = 0x423fad;
opencfw_hal_mspi_cq_term = 0x423f55;
opencfw_hal_delay_us = 0x41d1c1;
