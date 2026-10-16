#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
/* Link payload/gap regions around the existing source-owned metadata cells.
 * No second timestamp/offset state is introduced. See native_health_cache.ld. */
#define REGION(name,size) volatile uint8_t r1_cache_##name[size] __attribute__((section(".bss.r1.cache." #name),aligned(1)))
REGION(activity,576);REGION(activity_gap,2);
REGION(hr,72);REGION(hr_gap,6);
REGION(spo2,72);REGION(spo2_gap,6);
REGION(hrv,144);REGION(hrv_gap,10);
volatile uint8_t *r1_activity_daily_cache_accessor(void){return r1_cache_activity;}
volatile uint8_t *r1_hr_daily_cache_accessor(void){return r1_cache_hr;}
volatile uint8_t *r1_spo2_daily_cache_accessor(void){return r1_cache_spo2;}
volatile uint8_t *r1_hrv_daily_cache_accessor(void){return r1_cache_hrv;}
extern void __aeabi_memclr(void *,size_t);
static __attribute__((always_inline)) inline uint32_t reset(volatile uint8_t *base,uint32_t length,uint32_t timestamp,uint32_t offset,uint32_t timestamp_at)
{
 __aeabi_memclr((void *)(uintptr_t)base,length);
 write16(base+length,offset);write32(base+timestamp_at,timestamp);
 /* Native byte-clear postincrements r0 through the complete range. */
 return (uint32_t)(uintptr_t)base+length;
}
uint32_t r1_activity_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_activity,576,timestamp,offset,580);}
uint32_t r1_heart_rate_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_hr,72,timestamp,offset,80);}
uint32_t r1_spo2_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_spo2,72,timestamp,offset,80);}
uint32_t r1_hrv_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_hrv,144,timestamp,offset,156);}
