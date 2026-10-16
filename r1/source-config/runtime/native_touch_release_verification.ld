PROVIDE(r1_protocol_send_response = 0x20000205);
PROVIDE(osThreadFlagsSet = 0x20000209);
PROVIDE(r1_native_delayed_cancel = 0x2000020d);
PROVIDE(r1_touch_gesture_dispatch_boundary = 0x2000021d);
PROVIDE(r1_touch_task_message_boundary = 0x20000221);
PROVIDE(r1_structured_log_mode_get = 0x20000211);
PROVIDE(r1_structured_log_format = 0x20000215);
PROVIDE(nrf_log_frontend_std_1 = 0x20000219);
SECTIONS {
 .timer_code 0x934e4 : { *(.r1.touch.release.timer_code) }
 .contact 0x20016a60 : { *(.r1.touch.contact) }
 .pending 0x200067c4 : { *(.r1.touch.timer_pending) }
 .synthetic 0x200067c6 : { *(.r1.touch.synthetic_flag) }
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
