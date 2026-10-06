ENTRY(opencfw_boot_manager_start_wait)
opencfw_provider_4162c4 = 0x4162c5;
opencfw_provider_41652e = 0x41652f;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
