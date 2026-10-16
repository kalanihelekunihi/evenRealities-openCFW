PROVIDE(nrf_pwr_mgmt_shutdown = 0x20000301);
PROVIDE(r1_structured_log_mode_get = 0x20000305);
PROVIDE(r1_structured_log_format = 0x20000309);
PROVIDE(nrf_log_frontend_std_0 = 0x2000030d);
SECTIONS {
 .r1.dfu.context 0x2002c110 : { *(.r1.dfu.context) }
 .svci_state 0x2002c12c (NOLOAD) : { *(.bss.nrf_dfu_set_adv_name_svci_async_def) }
 .r1.dfu.adv_name 0x2002c138 : { *(.r1.dfu.adv_name) }
 .r1.dfu.backend_context 0x20007934 : { *(.r1.dfu.backend_context) }
 .r1.dfu.protected_ring 0xc2a98 : { *(.r1.dfu.protected_ring) }
 .r1.dfu.protected_sdk 0xc2b6c : { *(.r1.dfu.protected_sdk) }
 .r1.dfu.value_seed 0x9c65c : { *(.r1.dfu.value_seed) }
 .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) }
 .text 0x1000000 : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
