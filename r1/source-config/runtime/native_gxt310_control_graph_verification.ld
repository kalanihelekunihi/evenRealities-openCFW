SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .mode_error_ring 0x6f6b8 : { *(.r1.gxt.mode.error_ring) }
 .mode_error_sdk 0x6f700 : { *(.r1.gxt.mode.error_sdk) }
 .pair0_ring 0x51030 : { *(.r1.gxt.mode.pair0_ring) }
 .pair0_sdk 0x5105c : { *(.r1.gxt.mode.pair0_sdk) }
 .pair2_ring 0x51084 : { *(.r1.gxt.mode.pair2_ring) }
 .pair2_sdk 0x510b0 : { *(.r1.gxt.mode.pair2_sdk) }
 .id_ring 0x6f59c : { *(.r1.gxt.id.ring) }
 .id_sdk 0x6f5d4 : { *(.r1.gxt.id.sdk) }
 .name 0x50f20 : { *(.r1.gxt.bus.name) }
 .state 0x200076f8 (NOLOAD) : { *(.r1.gxt.bus.state) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_stock_registry_find = 0x20000201;
r1_stock_dispatch_08 = 0x20000211;
r1_stock_dispatch_0c = 0x20000221;
r1_stock_dispatch_10 = 0x20000231;
r1_stock_dispatch_14 = 0x20000241;
r1_structured_log_mode_get = 0x20000251;
r1_structured_log_format = 0x20000261;
nrf_log_frontend_std_0 = 0x20000271;
nrf_log_frontend_std_1 = 0x20000281;
nrf_log_frontend_std_2 = 0x20000291;
