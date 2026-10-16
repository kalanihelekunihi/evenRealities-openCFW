SECTIONS {
 .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) }
 .r1.bind.r1_motion_irq_device 0x200076b0 : { *(.r1.bind.r1_motion_irq_device) }
 .r1.bind.r1_motion_bus_device 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) }
 .r1.bind.r1_led_enable_device 0x20007688 : { *(.r1.bind.r1_led_enable_device) }
 .r1.bind.r1_touch_ldo_device 0x2000768c : { *(.r1.bind.r1_touch_ldo_device) }
 .r1.bind.r1_ppg_bus_device 0x200076cc : { *(.r1.bind.r1_ppg_bus_device) }
 .r1.bind.r1_ppg_irq_device 0x200076d0 : { *(.r1.bind.r1_ppg_irq_device) }
 .r1.bind.r1_ppg_reset_device 0x200076d8 : { *(.r1.bind.r1_ppg_reset_device) }
 .r1.bind.r1_touch_bus_device 0x200067fc : { *(.r1.bind.r1_touch_bus_device) }
 .r1.bind.r1_touch_output_device 0x20006800 : { *(.r1.bind.r1_touch_output_device) }
 .r1.bind.r1_touch_input_device 0x20006804 : { *(.r1.bind.r1_touch_input_device) }
 .r1.bind.name0 0x50144 : { *(.r1.bind.name0) }
 .r1.bind.name1 0x50168 : { *(.r1.bind.name1) }
 .r1.bind.name2 0x502e8 : { *(.r1.bind.name2) }
 .r1.bind.name3 0x502f4 : { *(.r1.bind.name3) }
 .r1.bind.name4 0x50978 : { *(.r1.bind.name4) }
 .r1.bind.name5 0x50980 : { *(.r1.bind.name5) }
 .r1.bind.name6 0x50988 : { *(.r1.bind.name6) }
 .r1.bind.name7 0x51340 : { *(.r1.bind.name7) }
 .r1.bind.name8 0x51348 : { *(.r1.bind.name8) }
 .r1.bind.name9 0x51358 : { *(.r1.bind.name9) }
 .text 0x1000000 : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
