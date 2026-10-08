ENTRY(opencfw_boot_delay_us_math)
opencfw_boot_rom_delay_cycles = 0x00000041;
SECTIONS { . = 0x10000; .text : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }
