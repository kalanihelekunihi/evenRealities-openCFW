ENTRY(opencfw_bl_clock_release_all)
clock_release = 0x422365;
SECTIONS { . = 0x00010000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
