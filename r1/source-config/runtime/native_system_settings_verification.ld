PROVIDE(r1_nv_modules_idle_check = 0x20000205);
PROVIDE(r1_protocol_send_checked = 0x20000209);
PROVIDE(r1_protocol_send_flag_set_c = 0x2000020d);
PROVIDE(r1_structured_log_mode_get = 0x20000211);
PROVIDE(r1_structured_log_format = 0x20000215);
PROVIDE(nrf_log_frontend_std_1 = 0x20000219);
PROVIDE(nrf_log_frontend_std_2 = 0x2000021d);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .get_ring 0x84630 : { *(.r1.settings.get_ring) }
 .get_sdk 0x84658 : { *(.r1.settings.get_sdk) }
 .set_ring 0x84678 : { *(.r1.settings.set_ring) }
 .set_sdk 0x846ac : { *(.r1.settings.set_sdk) }
 .devinfo 0x200069a8 : { *(.r1.battery.kv.devinfo) }
 .ble_mult 0x200069f4 : { *(.r1.nv.class.ble_mult) }
 .health 0x20006a68 : { *(.r1.nv.class.health) }
 .hsync 0x20006a8c : { *(.r1.nv.class.hsync) }
 .power 0x20006abc : { *(.r1.battery.kv.power) }
 .serial 0x20006ad8 : { *(.r1.serial.kv.class) }
 .r_size 0x20006b6c : { *(.r1.nv.class.r_size) }
 .handles 0x20007de8 : { *(.r1.nv.handles) }
 .port 0x20006974 : { *(.r1.kv.port_slot) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
