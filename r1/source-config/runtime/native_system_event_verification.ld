PROVIDE(r1_event_publish = 0x20000221);
PROVIDE(pvPortMalloc = 0x20000201);
PROVIDE(vPortFree = 0x20000205);
PROVIDE(r1_structured_log_mode_get = 0x20000209);
PROVIDE(r1_structured_log_format = 0x2000020d);
PROVIDE(nrf_log_frontend_std_1 = 0x20000211);
PROVIDE(nrf_log_frontend_std_2 = 0x20000215);
PROVIDE(nrf_log_frontend_std_4 = 0x20000219);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .alloc_ring 0x82a28 : { *(.r1.protocol_response.alloc_ring) }
 .alloc_sdk 0x82a54 : { *(.r1.protocol_response.alloc_sdk) }
 .tx_ring 0x82a7c : { *(.r1.protocol_response.tx_ring) }
 .tx_sdk 0x82ab8 : { *(.r1.protocol_response.tx_sdk) }
 .send_ring 0x82aec : { *(.r1.protocol_response.send_ring) }
 .send_sdk 0x82b24 : { *(.r1.protocol_response.send_sdk) }
 .phone 0x200064ba : { *(.r1.connection.field8) }
 .peer 0x200064bc : { *(.r1.connection.field10) }
 .sequence 0x20006b88 : { *(.r1.protocol.sequence) }
 .versions 0x20006ba0 : { *(.r1.protocol.version_map) }
 .hook 0x20006c20 : { *(.r1.protocol.send_hook) }
 .healthmode 0x2001e478 : { *(.r1.system.command.health_mode) }
 .wear_ring 0x84b9c : { *(.r1.system.command.wear_ring) }
 .wear_sdk 0x84bdc : { *(.r1.system.command.wear_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
