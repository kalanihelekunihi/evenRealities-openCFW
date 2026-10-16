/* Relocatable composition: one contiguous cache with existing metadata cells. */
SECTIONS {
 .r1.health.cache.activity : { *(.bss.r1.cache.activity) *(.r1.daily.activity.offset) *(.bss.r1.cache.activity_gap) *(.r1.daily.activity.timestamp) }
 .r1.health.cache.hr : { *(.bss.r1.cache.hr) *(.r1.daily.hr.offset) *(.bss.r1.cache.hr_gap) *(.r1.daily.hr.timestamp) }
 .r1.health.cache.spo2 : { *(.bss.r1.cache.spo2) *(.r1.daily.spo2.offset) *(.bss.r1.cache.spo2_gap) *(.r1.daily.spo2.timestamp) }
 .r1.health.cache.hrv : { *(.bss.r1.cache.hrv) *(.r1.daily.hrv.offset) *(.bss.r1.cache.hrv_gap) *(.r1.daily.hrv.timestamp) }
}
