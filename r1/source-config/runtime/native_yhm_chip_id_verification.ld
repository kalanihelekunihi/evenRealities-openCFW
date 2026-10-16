SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .bounds 0x35394 : { *(.r1.yhm.chip.bounds) }
 .success_ring 0x3539c : { *(.r1.yhm.chip.success_ring) }
 .success_sdk 0x353bc : { *(.r1.yhm.chip.success_sdk) }
 .error_ring 0x353d4 : { *(.r1.yhm.chip.error_ring) }
 .error_sdk 0x353f4 : { *(.r1.yhm.chip.error_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_yhm_register_read_native = 0x20000201;
r1_structured_log_mode_get = 0x20000211;
r1_structured_log_format = 0x20000221;
nrf_log_frontend_std_0 = 0x20000231;
