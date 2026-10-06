ENTRY(opencfw_hal_mspi_control)
opencfw_hal_delay_us = 0x41d1c1;
opencfw_hal_mspi_control_remaining = 0x08002221;
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
