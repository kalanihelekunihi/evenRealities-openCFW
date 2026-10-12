/* Authenticated partial absolute placement, with holes left absent. */
PHDRS { text PT_LOAD; alink PT_LOAD; llink PT_LOAD; lp PT_LOAD; active PT_LOAD; pm PT_LOAD; }
SECTIONS {
 .touch_ilo_callback 0xa1c0 : { KEEP(*(.text.touch_ilo_deep_sleep_callback)) } :text
 .active_slot_link 0x2000051c : AT(0xb5e8) {
  KEEP(*(.touch_init.active_slot_link))
 } :alink
 .lp_slot_link 0x20000520 : AT(0xb5ec) {
  KEEP(*(.touch_init.lp_slot_link))
 } :llink
 .lp_sensor_descriptors 0x20000808 : AT(0xb8d4) {
  KEEP(*(.touch_init.lp_sensor_descriptors))
 } :lp
 .active_sensor_descriptors 0x20000818 : AT(0xb8e4) {
  KEEP(*(.touch_init.active_sensor_descriptors))
 } :active
 .pm_descriptor 0x20000850 : AT(0xb91c) {
  KEEP(*(.touch_init.pm_descriptor))
 } :pm
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
 ASSERT(SIZEOF(.active_slot_link)==4,"active slot pointer")
 ASSERT(SIZEOF(.lp_slot_link)==4,"LP slot pointer")
 ASSERT(SIZEOF(.lp_sensor_descriptors)==16,"LP rows")
 ASSERT(SIZEOF(.active_sensor_descriptors)==20,"active rows")
 ASSERT(SIZEOF(.pm_descriptor)==28,"DeepSleep callback descriptor")
}
