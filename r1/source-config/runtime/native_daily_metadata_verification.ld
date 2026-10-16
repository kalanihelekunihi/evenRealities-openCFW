PROVIDE(r1_structured_log_mode_get = 0x20000201);
PROVIDE(r1_structured_log_format = 0x20000205);
PROVIDE(nrf_log_frontend_std_1 = 0x20000209);
SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .hr_ring 0x5ad60 : { *(.r1.daily.hr.ring) }
 .hr_sdk 0x5ad80 : { *(.r1.daily.hr.sdk) }
 .activity_ts 0x20016908 (NOLOAD) : { *(.r1.daily.activity.timestamp) }
 .activity_offset 0x20016904 (NOLOAD) : { *(.r1.daily.activity.offset) }
 .hr_ts 0x2001659c (NOLOAD) : { *(.r1.daily.hr.timestamp) }
 .hr_offset 0x20016594 (NOLOAD) : { *(.r1.daily.hr.offset) }
 .hrv_ts 0x20016a5c (NOLOAD) : { *(.r1.daily.hrv.timestamp) }
 .hrv_offset 0x20016a50 (NOLOAD) : { *(.r1.daily.hrv.offset) }
 .spo2_ts 0x200165f0 (NOLOAD) : { *(.r1.daily.spo2.timestamp) }
 .spo2_offset 0x200165e8 (NOLOAD) : { *(.r1.daily.spo2.offset) }
 .stress_ts 0x200166c0 (NOLOAD) : { *(.r1.daily.stress.timestamp) }
 .stress_offset 0x200166b8 (NOLOAD) : { *(.r1.daily.stress.offset) }
 .temperature_ts 0x20016644 (NOLOAD) : { *(.r1.daily.temperature.timestamp) }
 .temperature_offset 0x2001663c (NOLOAD) : { *(.r1.daily.temperature.offset) }
 .time_state 0x20016ac4 (NOLOAD) : { *(.r1.time.state) }
 .registration 0x20006820 (NOLOAD) : { *(.r1.time.registration) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
