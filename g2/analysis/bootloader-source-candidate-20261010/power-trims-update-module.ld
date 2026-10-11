ENTRY(event_a_power_trims_update)
event_a_power_ton_adjust = 0x08000101;
event_a_temperature_transition_separate = 0x08000111;
event_a_state_transition_sequence = 0x08000121;
SECTIONS {
  . = 0x430000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) }
}
