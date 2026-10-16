/* Verification-only callback endpoints; provider bodies are not supplied. */
PROVIDE(r1_led_ldo_device_bind = 0x20000201);
PROVIDE(r1_native_rtc_cached_device = 0x20000205);
PROVIDE(r1_vbat_adc_handle_cache = 0x20000209);
PROVIDE(r1_yhm_device_handles_initialize = 0x2000020d);
PROVIDE(r1_ppg_device_bind = 0x20000211);
PROVIDE(r1_motion_interrupt_input_lookup = 0x20000215);
PROVIDE(r1_touch_device_bind = 0x20000219);
PROVIDE(r1_i2c2_handle_cache = 0x2000021d);
PROVIDE(r1_i2c5_nfc_resource_registration = 0x20000221);
PROVIDE(r1_native_watchdog_hw_handle_init = 0x20000225);
SECTIONS { . = 0x01000000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
