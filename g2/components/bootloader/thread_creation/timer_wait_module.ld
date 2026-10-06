ENTRY(opencfw_boot_timer_wait_expiry)
opencfw_bl_remove_event_waiter = 0x41872d;
opencfw_bl_missed_yield = 0x4189a3;
opencfw_bl_timer_expire = 0x419407;
opencfw_bl_timer_rollover = 0x41965d;
opencfw_bl_timer_process_commands = 0x419547;
opencfw_bl_tick_increment = 0x418409;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
