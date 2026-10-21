ENTRY(opencfw_boot_main_callback)

opencfw_provider_416058 = 0x416059;
opencfw_provider_4160fe = 0x4160ff;
opencfw_provider_4160b0 = 0x4160b1;
opencfw_provider_41b2f8 = 0x41b2f9;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) }

  . = 0x433024;
  .rodata.manager_attributes : { KEEP(*(.rodata.manager_attributes)) }
  . = 0x434134;
  .rodata.manager_name : { KEEP(*(.rodata.manager_name)) }

  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
