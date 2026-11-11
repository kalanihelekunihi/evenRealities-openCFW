#include <stdint.h>
#include <stddef.h>
#include "../board/native_battery_memory.h"
/* Share sample writers/latest readers and daily metadata. Composition places
 * the existing prefix and timestamp contiguously; no duplicate cache owner. */
#define REGION(name,size) volatile uint8_t r1_cache_##name[size] __attribute__((section(".bss.r1.cache." #name),aligned(1)))
REGION(activity,576);REGION(activity_gap,2);
extern uint8_t r1_health_storage_hr_prefix[],r1_health_storage_spo2_prefix[],r1_health_storage_hrv_prefix[];
extern volatile uint32_t r1_daily_activity_timestamp,r1_daily_hr_timestamp,r1_daily_spo2_timestamp,r1_daily_hrv_timestamp;
#define r1_cache_hr r1_health_storage_hr_prefix
#define r1_cache_spo2 r1_health_storage_spo2_prefix
#define r1_cache_hrv r1_health_storage_hrv_prefix
volatile uint8_t *r1_activity_daily_cache_accessor(void){return r1_cache_activity;}
volatile uint8_t *r1_hr_daily_cache_accessor(void){return r1_cache_hr;}
volatile uint8_t *r1_spo2_daily_cache_accessor(void){return r1_cache_spo2;}
volatile uint8_t *r1_hrv_daily_cache_accessor(void){return r1_cache_hrv;}
extern void __aeabi_memclr(void *,size_t);
static __attribute__((always_inline)) inline uint32_t reset(volatile uint8_t *base,uint32_t length,uint32_t timestamp,uint32_t offset,volatile uint32_t *clock)
{
 __aeabi_memclr((void *)(uintptr_t)base,length);
 write16(base+length,offset);write32((volatile uint8_t *)clock,timestamp);
 /* Native byte-clear postincrements r0 through the complete range. */
 return (uint32_t)(uintptr_t)base+length;
}
uint32_t r1_activity_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_activity,576,timestamp,offset,&r1_daily_activity_timestamp);}
uint32_t r1_heart_rate_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_hr,72,timestamp,offset,&r1_daily_hr_timestamp);}
uint32_t r1_spo2_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_spo2,72,timestamp,offset,&r1_daily_spo2_timestamp);}
uint32_t r1_hrv_daily_cache_reset(uint32_t timestamp,uint32_t offset){return reset(r1_cache_hrv,144,timestamp,offset,&r1_daily_hrv_timestamp);}
