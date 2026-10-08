ENTRY(opencfw_boot_system_entry)
EXTERN(opencfw_boot_platform_configure)
EXTERN(opencfw_boot_storage_read)
EXTERN(opencfw_boot_storage_program)
EXTERN(opencfw_boot_storage_erase_validate)
EXTERN(opencfw_test_power_control_calls)
EXTERN(opencfw_test_accepted_power_object_calls)
PHDRS {
  source_text PT_LOAD FLAGS(5);
  expand_adapter PT_LOAD FLAGS(5);
  callbacks PT_LOAD FLAGS(5);
  source_431 PT_LOAD FLAGS(5);
  source_433 PT_LOAD FLAGS(5);
  source_434 PT_LOAD FLAGS(5);
}
opencfw_boot_platform_system_init = opencfw_boot_main_init;
opencfw_boot_platform_terminal = 0x4329c5;
opencfw_provider_41f9d8 = 0x41f9d9;
opencfw_provider_41f9f8 = 0x41f9f9;
opencfw_provider_41f846 = opencfw_boot_platform_configure + 1;
opencfw_provider_41ac44 = 0x41ac45;
opencfw_provider_41ac5a = 0x41ac5b;
opencfw_provider_41fa50 = 0x41fa51;
opencfw_provider_41e1e8 = 0x41e1e9;
opencfw_provider_41e266 = 0x41e267;
opencfw_provider_41ba80 = 0x41ba81;
opencfw_provider_415fae = 0x415faf;
opencfw_provider_41fd70 = 0x41fd71;
opencfw_provider_420476 = 0x420477;
opencfw_provider_421210 = 0x421211;
opencfw_provider_4176ce = 0x4176cf;
opencfw_boot_rom_mram_program = 0x0200ff21;
SECTIONS {
  . = 0x430a9c;
  .storage_read : { KEEP(*(.text.storage_read)) } :callbacks
  . = 0x430ac4;
  .storage_program : { KEEP(*(.text.storage_program)) } :callbacks
  . = 0x430aec;
  .storage_erase : { KEEP(*(.text.storage_erase)) } :callbacks

  . = 0x10000;
  .text : { *(.text*) *(.rodata) *(.rodata.register_*) *(.rodata.storage_*) *(.bss*) *(.test_data*) } :source_text

  . = 0x415326;
  .boot_expand_adapter : { KEEP(*(.boot_expand_adapter)) } :expand_adapter

  . = 0x431340;
  .rodata.main_file : { KEEP(*(.rodata.main_file)) } :source_431
  . = 0x43198c;
  .rodata.mode_error : { KEEP(*(.rodata.mode_error)) } :source_431
  . = 0x431e38;
  .boot_zero_adapter : { KEEP(*(.boot_zero_adapter)) } :source_431

  . = 0x433360;
  .rodata.boot_banner : { KEEP(*(.rodata.boot_banner)) } :source_433
  . = 0x433d98;
  .boot_platform_config : { KEEP(*(.boot_platform_config)) } :source_433

  . = 0x43401c;
  .boot_storage_range_table : { KEEP(*(.boot_storage_range_table)) } :source_434
  . = 0x43411c;
  .rodata.main_function : { KEEP(*(.rodata.main_function)) } :source_434
  . = 0x434124;
  .rodata.main_module : { KEEP(*(.rodata.main_module)) } :source_434

  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
