ENTRY(opencfw_spot_pcm22_transition1)
SECTIONS { . = 0x50000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) } }
