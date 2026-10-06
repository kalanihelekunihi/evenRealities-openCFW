ENTRY(opencfw_boot_event_thread)
opencfw_provider_416920 = 0x416921;
opencfw_provider_4168a2 = 0x4168a3;
opencfw_provider_4166aa = 0x4166ab;
opencfw_provider_416710 = 0x416711;
opencfw_provider_41649a = 0x41649b;
opencfw_provider_4160e8 = 0x4160e9;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
