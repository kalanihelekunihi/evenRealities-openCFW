ENTRY(opencfw_boot_cache_maintain)
PHDRS { source PT_LOAD FLAGS(5); }
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } :source /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
