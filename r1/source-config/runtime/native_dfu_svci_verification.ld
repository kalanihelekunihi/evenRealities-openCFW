SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .app_start 0x787f0 : { *(.r1.dfu.restore.app_start) }
 .info_ring 0x787f4 : { *(.r1.dfu.restore.info_ring) }
 .bounds 0x78824 : { *(.r1.dfu.restore.bounds) }
 .info_sdk 0x7882c : { *(.r1.dfu.restore.info_sdk) }
 .error_ring 0x78858 : { *(.r1.dfu.restore.error_ring) }
 .error_sdk 0x78894 : { *(.r1.dfu.restore.error_sdk) }
 .bss 0x2002c12c (NOLOAD) : { *(.bss.nrf_dfu_set_adv_name_svci_async_def) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
nrf_dfu_svci_vector_table_set = 0x20000201;
r1_structured_log_mode_get = 0x20000211;
r1_structured_log_format = 0x20000221;
nrf_log_frontend_std_0 = 0x20000231;
nrf_log_frontend_std_1 = 0x20000241;
