ENTRY(opencfw_boot_thread_new)
opencfw_bl_context_guard = 0x41602b;
opencfw_bl_kernel_static_thread = 0x417c7d;
opencfw_bl_kernel_dynamic_thread = 0x417d17;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
