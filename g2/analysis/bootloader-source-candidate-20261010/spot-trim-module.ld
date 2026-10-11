ENTRY(native_spot_profile_trim_42ae24)
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
