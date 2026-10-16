PROVIDE(r1_protocol_send_response = 0x20000205);
PROVIDE(osThreadFlagsSet = 0x20000209);
PROVIDE(r1_touch_synthetic_release_boundary = 0x2000020d);
PROVIDE(r1_structured_log_mode_get = 0x20000211);
PROVIDE(r1_structured_log_format = 0x20000215);
PROVIDE(nrf_log_frontend_std_1 = 0x20000219);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .clients 0x200067d8 : { *(.r1.touch.clients) }
 .thread 0x2000666c : { *(.r1.touch.thread) }
 .close_ring 0x8e708 : { *(.r1.touch.close.ring) }
 .close_sdk 0x8e738 : { *(.r1.touch.close.sdk) }
 .open_ring 0x8e834 : { *(.r1.touch.open.ring) }
 .open_sdk 0x8e860 : { *(.r1.touch.open.sdk) }
 .phone_ring 0x84934 : { *(.r1.touch.switch.phone_ring) }
 .phone_sdk 0x8496c : { *(.r1.touch.switch.phone_sdk) }
 .glasses_ring 0x849a0 : { *(.r1.touch.switch.glasses_ring) }
 .glasses_sdk 0x849dc : { *(.r1.touch.switch.glasses_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
