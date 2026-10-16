PROVIDE(r1_advertising_configuration_byte_get = 0x20000201);
PROVIDE(r1_battery_runtime_update_service = 0x20000205);
PROVIDE(r1_structured_log_local_timestamp = 0x20000209);
PROVIDE(vPortEnterCritical = 0x2000020d);
PROVIDE(vPortExitCritical = 0x20000211);
PROVIDE(r1_event_publish = 0x20000215);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .read 0x20006938 : { *(.r1.status.read) }
 .write 0x20006939 : { *(.r1.status.write) }
 .dropped 0x2000693c : { *(.r1.status.dropped) }
 .records 0x20019bc8 : { *(.r1.status.records) }
 .device2c 0x20016bb0 : { *(.r1.status.device2c) }
 .device2d 0x20016bb1 : { *(.r1.status.device2d) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
 .glasses 0x200064bc : { *(.r1.connection.field10) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
