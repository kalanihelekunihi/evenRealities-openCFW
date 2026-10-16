SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .bounds 0x351ec : { *(.r1.device.checks.bounds) }
 .error_ring 0x351f4 : { *(.r1.device.checks.error_ring) }
 .error_sdk 0x35214 : { *(.r1.device.checks.error_sdk) }
 .success_ring 0x3522c : { *(.r1.device.checks.success_ring) }
 .success_sdk 0x3524c : { *(.r1.device.checks.success_sdk) }
 .delay 0x35264 : { *(.r1.device.checks.delay) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_yhm_chip_id_native = 0x20000201;
r1_yhm_register_write_native = 0x20000211;
r1_rtt_delay_cycles = 0x20000221;
r1_structured_log_mode_get = 0x20000231;
r1_structured_log_format = 0x20000241;
nrf_log_frontend_std_0 = 0x20000251;
r1_gxt310_bus_acquire = 0x20000261;
r1_gxt310_enable_pair_native = 0x20000271;
r1_gxt310_chip_id_channel0 = 0x20000281;
r1_gxt310_chip_id_channel2 = 0x20000291;
r1_gxt310_disable_pair_native = 0x200002a1;
r1_gxt310_bus_release = 0x200002b1;
