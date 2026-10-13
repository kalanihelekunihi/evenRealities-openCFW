SECTIONS {
 .common 0xb2a8 : { *(.touch_rom.common_config) }
 .electrodes 0xb2e4 : { *(.touch_rom.electrodes) }
 .shield_electrodes 0xb32c : { *(.touch_rom.shield_electrodes) }
 .shield_pins 0xb33c : { *(.touch_rom.shield_pins) }
 .pins 0xb34c : { *(.touch_rom.pin_config) }
 .channel 0x2000082c : { *(.touch_init.pending_channel) }
 .driver 0x20000cc8 (NOLOAD) : { *(.touch_bss.msclp_context) }
 ASSERT(SIZEOF(.common)==60,"common extent")
 ASSERT(SIZEOF(.electrodes)==72,"nine electrodes")
 ASSERT(SIZEOF(.pins)==40,"five pins")
}
