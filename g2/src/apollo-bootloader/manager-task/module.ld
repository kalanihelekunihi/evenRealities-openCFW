ENTRY(opencfw_boot_manager_task)
opencfw_provider_42e254 = 0x42e255;
opencfw_provider_42e278 = 0x42e279;
opencfw_provider_42e2ea = 0x42e2eb;
opencfw_provider_4162c4 = 0x4162c5;
opencfw_provider_4160e8 = 0x4160e9;
opencfw_provider_42dca2 = 0x42dca3;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
