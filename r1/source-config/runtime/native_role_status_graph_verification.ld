PROVIDE(r1_structured_log_mode_get = 0x20000201);
PROVIDE(r1_structured_log_format = 0x20000205);
PROVIDE(nrf_log_frontend_std_1 = 0x20000209);
PROVIDE(nrf_log_frontend_std_2 = 0x2000020d);
PROVIDE(nrf_log_frontend_std_3 = 0x20000211);
PROVIDE(osDelay = 0x20000215);
PROVIDE(r1_retained_log_printf_sink = 0x20000219);
PROVIDE(r1_advertising_configuration_byte_get = 0x20000231);
PROVIDE(r1_battery_runtime_update_service = 0x20000235);
PROVIDE(r1_structured_log_local_timestamp = 0x20000239);
PROVIDE(vPortEnterCritical = 0x2000023d);
PROVIDE(vPortExitCritical = 0x20000241);
PROVIDE(r1_event_publish = 0x20000245);
PROVIDE(r1_phone_role_assertion_stack_transfer = 0x20000221);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .text0 0xbe110 : { *(.r1.phone.role.text0) }
 .text1 0xbe15c : { *(.r1.phone.role.text1) }
 .text2 0x4dbec : { *(.r1.phone.role.text2) }
 .text3 0x4dc18 : { *(.r1.phone.role.text3) }
 .text4 0xbdc48 : { *(.r1.phone.role.text4) }
 .text5 0x4dc40 : { *(.r1.phone.role.text5) }
 .text6 0x4dc80 : { *(.r1.phone.role.text6) }
 .text7 0x4dc94 : { *(.r1.phone.role.text7) }
 .text8 0x4dcbc : { *(.r1.phone.role.text8) }
 .text9 0x4dcc8 : { *(.r1.phone.role.text9) }
 .text10 0x99118 : { *(.r1.phone.role.text10) }
 .text11 0x4dcd8 : { *(.r1.phone.role.text11) }
 .text12 0x4dce8 : { *(.r1.phone.role.text12) }
 .text13 0x4dcec : { *(.r1.phone.role.text13) }
 .text14 0x4dd00 : { *(.r1.phone.role.text14) }
 .text15 0x4dd20 : { *(.r1.phone.role.text15) }
 .text16 0xbdfac : { *(.r1.phone.role.text16) }
 .text17 0x4dd3c : { *(.r1.phone.role.text17) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
 .glasses 0x200064bc : { *(.r1.connection.field10) }
 .read 0x20006938 : { *(.r1.status.read) }
 .write 0x20006939 : { *(.r1.status.write) }
 .dropped 0x2000693c : { *(.r1.status.dropped) }
 .records 0x20019bc8 : { *(.r1.status.records) }
 .device2c 0x20016bb0 : { *(.r1.status.device2c) }
 .device2d 0x20016bb1 : { *(.r1.status.device2d) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
