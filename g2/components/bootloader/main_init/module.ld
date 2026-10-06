ENTRY(opencfw_boot_main_init)
PHDRS {
  text PT_LOAD FLAGS(5);
  strings PT_LOAD FLAGS(4);
}

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
  .text : { *(.text*) } :text

  . = 0x431340;
  .rodata.main_file : { KEEP(*(.rodata.main_file)) } :strings
  . = 0x43198c;
  .rodata.mode_error : { KEEP(*(.rodata.mode_error)) } :strings
  . = 0x433360;
  .rodata.boot_banner : { KEEP(*(.rodata.boot_banner)) } :strings
  . = 0x43411c;
  .rodata.main_function : { KEEP(*(.rodata.main_function)) } :strings
  . = 0x434124;
  .rodata.main_module : { KEEP(*(.rodata.main_module)) } :strings

  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
