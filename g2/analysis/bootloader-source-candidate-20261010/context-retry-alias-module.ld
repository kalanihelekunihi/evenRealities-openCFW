ENTRY(opencfw_bl_config_retry)
opencfw_bl_power_register_update = 0x41d92d;
opencfw_boot_delay_scaled = 0x41f9d9;
opencfw_boot_context_transaction = 0x42c989;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
