ENTRY(opencfw_pcm22_spot_timer_start)
clock_request = 0x08000101;
clock_release = 0x08000111;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
