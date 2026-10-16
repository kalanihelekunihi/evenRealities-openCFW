PROVIDE(r1_protocol_send_response = 0x20000201);
PROVIDE(nrf_log_frontend_std_1 = 0x20000205);
PROVIDE(r1_structured_log_mode_get = 0x20000209);
PROVIDE(r1_structured_log_format = 0x2000020d);
PROVIDE(nrf_log_frontend_std_2 = 0x20000211);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .devinfo 0x200069a8 : { *(.r1.battery.kv.devinfo) }
 .ble_mult 0x200069f4 : { *(.r1.nv.class.ble_mult) }
 .health 0x20006a68 : { *(.r1.nv.class.health) }
 .hsync 0x20006a8c : { *(.r1.nv.class.hsync) }
 .power 0x20006abc : { *(.r1.battery.kv.power) }
 .serial 0x20006ad8 : { *(.r1.serial.kv.class) }
 .r_size 0x20006b6c : { *(.r1.nv.class.r_size) }
 .handles 0x20007de8 : { *(.r1.nv.handles) }
 .port 0x20006974 : { *(.r1.kv.port_slot) }
 .ring 0x73580 : { *(.r1.nv.sync.ring) }
 .sdk 0x735b4 : { *(.r1.nv.sync.sdk) }
 .writer_ring 0x917fc : { *(.r1.nv.class_writer.ring) }
 .writer_sdk 0x91838 : { *(.r1.nv.class_writer.sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
