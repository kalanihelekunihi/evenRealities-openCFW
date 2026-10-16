PROVIDE(osMessageQueuePut = 0x20000205);
PROVIDE(osThreadFlagsSet = 0x20000209);
PROVIDE(r1_structured_log_mode_get = 0x2000020d);
PROVIDE(r1_structured_log_format = 0x20000211);
PROVIDE(nrf_log_frontend_std_0 = 0x20000215);
SECTIONS {
 .timer_code 0x934e4 : { *(.r1.touch.release.timer_code) }
 .thread 0x2000666c : { *(.r1.touch.thread) }
 .queue 0x20006670 : { *(.r1.touch.task.queue) }
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .null_ring 0x935b8 : { *(.r1.touch.task.null_ring) }
 .null_sdk 0x935e4 : { *(.r1.touch.task.null_sdk) }
 .missed_ring 0x93608 : { *(.r1.touch.task.missed_ring) }
 .missed_sdk 0x9361c : { *(.r1.touch.task.missed_sdk) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
