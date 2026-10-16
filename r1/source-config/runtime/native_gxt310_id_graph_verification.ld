SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .ring 0x6f59c : { *(.r1.gxt.id.ring) }
 .bounds 0x6f5cc : { *(.r1.gxt.id.bounds) }
 .sdk 0x6f5d4 : { *(.r1.gxt.id.sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_gxt310_register_read_native = 0x20000201;
r1_structured_log_mode_get = 0x20000211;
r1_structured_log_format = 0x20000221;
nrf_log_frontend_std_2 = 0x20000231;

r1_gxt310_bus_acquire = 0x20000241;
r1_gxt310_enable_pair_native = 0x20000251;
r1_gxt310_disable_pair_native = 0x20000261;
r1_gxt310_bus_release = 0x20000271;
