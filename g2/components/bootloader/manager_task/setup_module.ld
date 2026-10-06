ENTRY(opencfw_provider_42e254)
opencfw_boot_manager_event_init = opencfw_provider_42e254;
opencfw_boot_manager_setup = opencfw_provider_42e278;
opencfw_boot_manager_signal_dfu = opencfw_provider_42e2ea;
opencfw_provider_4164da = 0x4164db;
opencfw_provider_42e53c = 0x42e53d;
opencfw_provider_41623a = 0x41623b;
opencfw_provider_416590 = 0x416591;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
