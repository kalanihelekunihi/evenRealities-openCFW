/* Verification-only provider endpoints. No callee executable bodies supplied. */
PROVIDE(nrf_log_init = 0x20000201);
PROVIDE(r1_adc_error = 0x20000205);
PROVIDE(nrf_log_default_backends_init = 0x20000209);
PROVIDE(cm_backtrace_init = 0x2000020d);
PROVIDE(ble_dfu_buttonless_async_svci_init = 0x20000211);
PROVIDE(nrf_drv_clock_init = 0x20000215);
PROVIDE(r1_boot_ctor_run = 0x20000219);
PROVIDE(r1_peripheral_module_init = 0x2000021d);
PROVIDE(r1_device_module_init = 0x20000221);
PROVIDE(r1_structured_log_mode_get = 0x20000225);
PROVIDE(r1_structured_log_format = 0x20000229);
PROVIDE(nrf_log_frontend_std_0 = 0x2000022d);
PROVIDE(r1_reset_reason_nordic_adapter = 0x20000231);
SECTIONS {
 . = 0x75ff8; .r1.app.entry.scr : { *(.r1.app.entry.scr) }
 . = 0x75ffc; .r1.app.entry.version : { *(.r1.app.entry.version) }
 . = 0x76008; .r1.app.entry.hardware : { *(.r1.app.entry.hardware) }
 . = 0x76014; .r1.app.entry.build : { *(.r1.app.entry.build) }
 . = 0x76040; .r1.app.entry.ring : { *(.r1.app.entry.ring) }
 . = 0x76060; .r1.app.entry.log_bounds : { *(.r1.app.entry.log_bounds) }
 . = 0x76068; .r1.app.entry.sdk : { *(.r1.app.entry.sdk) }
 . = 0x76084; .r1.app.entry.callback_cell : { *(.r1.app.entry.callback_cell) }
 . = 0x01000000; .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
