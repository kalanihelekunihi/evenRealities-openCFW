ENTRY(opencfw_boot_itcm_countdown)
SECTIONS { . = 0x40; .text : { *(.text.itcm_helpers) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
