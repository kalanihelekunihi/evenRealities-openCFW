SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .word 0x6f6b4 : { *(.r1.gxt.mode.word) }
 .error_ring 0x6f6b8 : { *(.r1.gxt.mode.error_ring) }
 .bounds 0x6f6f8 : { *(.r1.gxt.mode.bounds) }
 .error_sdk 0x6f700 : { *(.r1.gxt.mode.error_sdk) }
 .pair_bounds 0x51028 : { *(.r1.gxt.mode.pair_bounds) }
 .pair0_ring 0x51030 : { *(.r1.gxt.mode.pair0_ring) }
 .pair0_sdk 0x5105c : { *(.r1.gxt.mode.pair0_sdk) }
 .pair2_ring 0x51084 : { *(.r1.gxt.mode.pair2_ring) }
 .pair2_sdk 0x510b0 : { *(.r1.gxt.mode.pair2_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_gxt310_register_write_native = 0x20000201;
r1_structured_log_mode_get = 0x20000211;
r1_structured_log_format = 0x20000221;
nrf_log_frontend_std_0 = 0x20000231;
nrf_log_frontend_std_1 = 0x20000241;
