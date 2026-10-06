ENTRY(opencfw_boot_system_entry)

PHDRS {
  source_text PT_LOAD FLAGS(5);
  expand_adapter PT_LOAD FLAGS(5);
  source_path PT_LOAD FLAGS(4);
  error_string PT_LOAD FLAGS(4);
  zero_adapter PT_LOAD FLAGS(5);
  banner_string PT_LOAD FLAGS(4);
  function_string PT_LOAD FLAGS(4);
  module_string PT_LOAD FLAGS(4);
}

opencfw_boot_platform_system_init = opencfw_boot_main_init;
opencfw_boot_platform_terminal = 0x4329c5;

opencfw_provider_41f9d8 = 0x41f9d9;
opencfw_provider_41f9f8 = 0x41f9f9;
opencfw_provider_41f846 = 0x41f847;
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

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata) } :source_text

  . = 0x415326;
  .boot_expand_adapter : { KEEP(*(.boot_expand_adapter)) } :expand_adapter

  . = 0x431340;
  .rodata.main_file : { KEEP(*(.rodata.main_file)) } :source_path

  . = 0x43198c;
  .rodata.mode_error : { KEEP(*(.rodata.mode_error)) } :error_string

  . = 0x431e38;
  .boot_zero_adapter : { KEEP(*(.boot_zero_adapter)) } :zero_adapter

  . = 0x433360;
  .rodata.boot_banner : { KEEP(*(.rodata.boot_banner)) } :banner_string

  . = 0x43411c;
  .rodata.main_function : { KEEP(*(.rodata.main_function)) } :function_string

  . = 0x434124;
  .rodata.main_module : { KEEP(*(.rodata.main_module)) } :module_string

  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
