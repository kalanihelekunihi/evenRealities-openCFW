ENTRY(opencfw_boot_scheduler_bootstrap)
PHDRS { text PT_LOAD FLAGS(5); names PT_LOAD FLAGS(4); timer_name PT_LOAD FLAGS(4); }
opencfw_boot_scheduler_bootstrap = opencfw_bl_kernel_start;
opencfw_bl_kernel_dynamic_thread = 0x417d17;
opencfw_bl_port_start = 0x41b4f7;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } :text
. = 0x43412c; .boot_idle_name : { KEEP(*(.boot_idle_name)) } :names
. = 0x43413c; .boot_timer_name : { KEEP(*(.boot_timer_name)) } :timer_name
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
