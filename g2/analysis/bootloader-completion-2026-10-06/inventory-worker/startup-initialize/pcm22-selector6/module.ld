SECTIONS { . = 0x08010000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_hal_delay_us = 0x1ecc1;
opencfw_pcm22_timer_service = 0x312d9;
event_a_power_ton_adjust = 0x313b1;
