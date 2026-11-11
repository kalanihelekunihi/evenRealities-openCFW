/* Relocatable composition: one contiguous cache with existing metadata cells. */
SECTIONS {
 .r1.health.cache.activity : { KEEP(*(.bss.r1.cache.activity)) KEEP(*(.r1.daily.activity.offset)) KEEP(*(.bss.r1.cache.activity_gap)) KEEP(*(.r1.daily.activity.timestamp)) }
 .r1.health.cache.hr : { KEEP(*(.r1.health.storage.hr)) KEEP(*(.r1.daily.hr.timestamp)) }
 .r1.health.cache.spo2 : { KEEP(*(.r1.health.storage.spo2)) KEEP(*(.r1.daily.spo2.timestamp)) }
 .r1.health.cache.hrv : { KEEP(*(.r1.health.storage.hrv)) KEEP(*(.r1.daily.hrv.timestamp)) }
 .r1.health.cache.temperature : { KEEP(*(.r1.health.storage.temperature)) KEEP(*(.r1.daily.temperature.timestamp)) }
 .r1.health.cache.stress : { KEEP(*(.r1.health.hourly_stress)) KEEP(*(.r1.daily.stress.timestamp)) }
}
