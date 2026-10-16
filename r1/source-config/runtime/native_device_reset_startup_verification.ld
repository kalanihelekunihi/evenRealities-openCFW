/* Typed external verification endpoints only; no provider bodies supplied. */
PROVIDE(r1_device_preinitialize_3510c = 0x20000201);
PROVIDE(r1_gxt310_self_check = 0x20000205);
PROVIDE(r1_reset_reason_decode_and_report = 0x20000209);
PROVIDE(r1_stock_dispatch_08 = 0x2000020d);
PROVIDE(r1_stock_dispatch_20 = 0x20000211);
PROVIDE(r1_structured_log_mode_get = 0x20000215);
PROVIDE(r1_structured_log_format = 0x20000219);
PROVIDE(nrf_log_frontend_std_0 = 0x2000021d);
PROVIDE(nrf_log_frontend_std_1 = 0x20000221);
PROVIDE(r1_structured_rtc_device = 0x20007690);
SECTIONS {
 . = 0x4e968; .r1.device.startup.check_state : { *(.r1.device.startup.check_state) }
 . = 0x4e96c; .r1.device.startup.check_ring : { *(.r1.device.startup.check_ring) }
 . = 0x4e994; .r1.device.startup.check_bounds : { *(.r1.device.startup.check_bounds) }
 . = 0x4e99c; .r1.device.startup.check_sdk : { *(.r1.device.startup.check_sdk) }
 . = 0x4ea08; .r1.device.startup.rtc_callback : { *(.r1.device.startup.rtc_callback) }
 . = 0x4ea0c; .r1.device.startup.rtc_cache : { *(.r1.device.startup.rtc_cache) }
 . = 0x4ea10; .r1.device.startup.rtc_noop : { *(.r1.device.startup.rtc_noop) }
 . = 0x5c514; .r1.device.startup.device_ring : { *(.r1.device.startup.device_ring) }
 . = 0x5c53c; .r1.device.startup.device_bounds : { *(.r1.device.startup.device_bounds) }
 . = 0x5c544; .r1.device.startup.device_sdk : { *(.r1.device.startup.device_sdk) }
 . = 0x77ee8; .r1.device.startup.reset_register : { *(.r1.device.startup.reset_register) }
 . = 0x77eec; .r1.device.startup.reset_ring : { *(.r1.device.startup.reset_ring) }
 . = 0x77f0c; .r1.device.startup.reset_bounds : { *(.r1.device.startup.reset_bounds) }
 . = 0x77f14; .r1.device.startup.reset_sdk : { *(.r1.device.startup.reset_sdk) }
 . = 0x77f2c; .r1.device.startup.reset_cache : { *(.r1.device.startup.reset_cache) }
 . = 0x01000000; .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
