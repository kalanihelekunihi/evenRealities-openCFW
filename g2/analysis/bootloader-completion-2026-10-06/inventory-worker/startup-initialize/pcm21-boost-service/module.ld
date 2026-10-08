SECTIONS { . = 0x08010000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_control_critical_save = 0x171a5;
native_spot_trim_restore_42ae6c = 0x30885;
native_spot_profile_trim_42ae24 = 0x30839;
opencfw_pcm22_spot_timer_stop = 0x310a5;
