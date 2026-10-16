PROVIDE(pvPortMalloc = 0x20000201);
PROVIDE(vPortFree = 0x20000205);
PROVIDE(osMessageQueuePut = 0x20000209);
PROVIDE(osThreadFlagsSet = 0x2000020d);
PROVIDE(r1_structured_log_mode_get = 0x20000211);
PROVIDE(r1_structured_log_format = 0x20000215);
PROVIDE(nrf_log_frontend_std_0 = 0x20000219);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .log0 0x33990 : { *(.r1.ble.message.log0) }
 .log1 0x339bc : { *(.r1.ble.message.log1) }
 .log2 0x339e4 : { *(.r1.ble.message.log2) }
 .log3 0x33a14 : { *(.r1.ble.message.log3) }
 .log4 0x33a3c : { *(.r1.ble.message.log4) }
 .log5 0x33a64 : { *(.r1.ble.message.log5) }
 .log6 0x33a88 : { *(.r1.ble.message.log6) }
 .log7 0x33ab8 : { *(.r1.ble.message.log7) }
 .thread 0x20006570 (NOLOAD) : { *(.r1.control.service.thread) }
 .queue 0x20006574 (NOLOAD) : { *(.r1.ble.message.queue) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
