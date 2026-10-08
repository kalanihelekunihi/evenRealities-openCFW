ENTRY(step_ticks)
SECTIONS { .text 0x08000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }


deep_sleep = 0x0800e051;cleanup = 0x0800e061;
reschedule = 0x0800e071;suspend_scheduler = 0x0800e081;
resume_scheduler = 0x0800e091;

