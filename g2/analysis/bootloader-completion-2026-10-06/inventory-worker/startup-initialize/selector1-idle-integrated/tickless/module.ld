ENTRY(tickless_sleep)
SECTIONS { .  =  0x50000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) } }
confirm_sleep = 0x08000101;counter_read = 0x08000111;timer_compare = 0x08000121;pre_sleep = 0x08000131;post_sleep = 0x08000141;timer_enable = 0x08000151;irq_clear = 0x08000161;step_ticks = 0x08000171;
