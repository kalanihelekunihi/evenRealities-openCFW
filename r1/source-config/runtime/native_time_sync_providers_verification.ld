PROVIDE(r1_ble_thread_message_encode = 0x20000205);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
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
