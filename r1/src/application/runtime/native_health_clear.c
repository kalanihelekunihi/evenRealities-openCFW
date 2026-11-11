/* Locked R1 2.2.6.0009: clear-all orchestration 0x8b184 and DB getter 0x70028. */
#include "native_health_database.h"
#include "../board/native_battery_memory.h"
#include <stddef.h>
extern void r1_sleep_storage_delete_all(void);
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_time_local_day_start(void),r1_health_record_write(const void *);
extern volatile uint8_t *r1_hr_daily_cache_accessor(void),*r1_spo2_daily_cache_accessor(void),*r1_temperature_daily_cache_accessor(void),*r1_stress_daily_cache_accessor(void),*r1_activity_daily_cache_accessor(void),*r1_hrv_daily_cache_accessor(void);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern fdb_tsdb_t r1_health_sync_provider_00070028(void);
static void diagnostic(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003u,sdk);
}
static void clear_scalar(volatile uint8_t *cache,uint32_t day,uint32_t offset)
{
 if(!cache)return;
 __aeabi_memclr((void *)(uintptr_t)cache,72);
 /* Retain byte74; stock clears only this unaligned tail. */
 write32(cache+75,0);cache[79]=0;
 write16(cache+72,offset);write32(cache+80,day);
}
void r1_health_clear_all_caches(void)
{
 diagnostic("[RING]service_health_clear_all_data: start","service_health_clear_all_data: start");
 fdb_tsdb_t db=r1_health_sync_provider_00070028();
 if(db)fdb_tsl_clean(db);
 r1_sleep_storage_delete_all();
 uint32_t offset=(uint16_t)r1_time_utc_offset_get();
 uint32_t day=r1_time_local_day_start();
 clear_scalar(r1_hr_daily_cache_accessor(),day,offset);
 clear_scalar(r1_spo2_daily_cache_accessor(),day,offset);
 clear_scalar(r1_temperature_daily_cache_accessor(),day,offset);
 clear_scalar(r1_stress_daily_cache_accessor(),day,offset);
 volatile uint8_t *cache=r1_activity_daily_cache_accessor();
 if(cache){
  __aeabi_memclr((void *)(uintptr_t)cache,576);
  write16(cache+576,offset);write32(cache+580,day);
 }
 cache=r1_hrv_daily_cache_accessor();
 if(cache){
  __aeabi_memclr((void *)(uintptr_t)cache,144);
  write32(cache+147,0);write16(cache+151,0);
  write16(cache+144,offset);write32(cache+156,day);
 }
 uint32_t record[6];__aeabi_memclr(record,sizeof(record));
 (void)r1_health_record_write(record);
 diagnostic("[RING]service_health_clear_all_data: done","service_health_clear_all_data: done");
}
