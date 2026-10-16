PROVIDE(r1_touch_release_timer_callback = 0x934e5);
PROVIDE(r1_native_delayed_schedule = 0x20000205);
PROVIDE(r1_reset_trace_reboot_caller_write = 0x20000209);
PROVIDE(osThreadFlagsSet = 0x2000020d);
PROVIDE(osKernelGetTickCount = 0x20000211);
PROVIDE(r1_advertising_configuration_byte_get = 0x20000215);
PROVIDE(r1_glasses_connection_handle_get = 0x20000219);
PROVIDE(r1_ble_tx_queue_dispatch_type0 = 0x2000021d);
PROVIDE(r1_structured_log_mode_get = 0x20000221);
PROVIDE(r1_structured_log_format = 0x20000225);
PROVIDE(nrf_log_frontend_std_0 = 0x20000229);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .contact 0x20016a60 : { *(.r1.touch.contact) }
 .pending 0x200067c4 : { *(.r1.touch.timer_pending) }
 .direction 0x200067c5 : { *(.r1.touch.gesture.direction) }
 .synthetic 0x200067c6 : { *(.r1.touch.synthetic_flag) }
 .count 0x200067cc : { *(.r1.touch.gesture.count) }
 .clients 0x200067d8 : { *(.r1.touch.clients) }
 .time 0x200067dc : { *(.r1.touch.gesture.time) }
 .up_time 0x200067e0 : { *(.r1.touch.gesture.up_time) }
 .down_time 0x200067e4 : { *(.r1.touch.gesture.down_time) }
 .thread 0x20006548 : { *(.r1.battery.low.thread) }
 .reset_ring 0x3ebfc : { *(.r1.touch.gesture.reset_ring) }
 .reset_sdk 0x3ec20 : { *(.r1.touch.gesture.reset_sdk) }
 .single_ring 0xbfcd8 : { *(.r1.touch.gesture.single_ring) }
 .single_sdk 0xbfd40 : { *(.r1.touch.gesture.single_sdk) }
 .double_ring 0xbfc10 : { *(.r1.touch.gesture.double_ring) }
 .double_sdk 0xbfc78 : { *(.r1.touch.gesture.double_sdk) }
 .long_ring 0xbff24 : { *(.r1.touch.gesture.long_ring) }
 .long_sdk 0xbff88 : { *(.r1.touch.gesture.long_sdk) }
 .up_ring 0xbfe64 : { *(.r1.touch.gesture.up_ring) }
 .up_sdk 0xbfec8 : { *(.r1.touch.gesture.up_sdk) }
 .down_ring 0xbfda0 : { *(.r1.touch.gesture.down_ring) }
 .down_sdk 0xbfe04 : { *(.r1.touch.gesture.down_sdk) }
 .release_ring 0xbfb40 : { *(.r1.touch.gesture.release_ring) }
 .release_sdk 0xbfbac : { *(.r1.touch.gesture.release_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
