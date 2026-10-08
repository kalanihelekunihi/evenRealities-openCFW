ENTRY(step_ticks)
SECTIONS { .text 0x08000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }


cleanup = opencfw_boot_idle_cleanup;
reschedule = opencfw_bl_kernel_reschedule;suspend_scheduler = opencfw_bl_scheduler_suspend;
resume_scheduler = opencfw_bl_scheduler_resume;


  power_state = 0x0800d021;
buck_override = opencfw_boot_ton_gate_write;  
delay_one = 0x0800d061; boost_service = 0x0800d071;
