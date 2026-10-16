#include <stdint.h>
#include "time_calendar/time_calendar.h"
extern time_calendar_state r1_time_state;
extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
/* Individual authenticated fields, not complete cache structures. */
#define CELL(name) volatile uint32_t r1_daily_##name##_timestamp __attribute__((section(".r1.daily." #name ".timestamp"),aligned(4)))=0; volatile uint16_t r1_daily_##name##_offset __attribute__((section(".r1.daily." #name ".offset"),aligned(2)))=0
CELL(activity);CELL(hr);CELL(hrv);CELL(spo2);CELL(stress);CELL(temperature);
const char r1_daily_hr_ring[] __attribute__((section(".r1.daily.hr.ring")))="[RING]hr db init: %d";
const char r1_daily_hr_sdk[] __attribute__((section(".r1.daily.hr.sdk")))="hr db init: %d";
__attribute__((noinline)) uint32_t r1_time_local_day_start(void)
{
 int32_t offset=(int32_t)r1_time_state.utc_offset_minutes*60;
 uint64_t adjusted=(uint64_t)(int64_t)offset+r1_time_backend_timestamp();
 return (uint32_t)((adjusted/86400u)*86400u)-(uint32_t)offset;
}
__attribute__((noinline)) int32_t r1_time_utc_offset_get(void){return r1_time_state.utc_offset_minutes;}
#define REFRESH(name) __attribute__((noinline)) uint32_t r1_daily_##name##_refresh(void){r1_daily_##name##_timestamp=r1_time_local_day_start();int32_t offset=r1_time_utc_offset_get();r1_daily_##name##_offset=(uint16_t)offset;return (uint32_t)offset;}
REFRESH(activity) REFRESH(hrv) REFRESH(spo2) REFRESH(temperature)
__attribute__((noinline)) uint32_t r1_daily_stress_refresh(void)
{r1_daily_stress_timestamp=r1_time_backend_timestamp();int32_t offset=r1_time_utc_offset_get();r1_daily_stress_offset=(uint16_t)offset;return (uint32_t)offset;}
__attribute__((noinline)) uint32_t r1_daily_hr_refresh(void)
{
 r1_daily_hr_timestamp=r1_time_local_day_start();r1_daily_hr_offset=(uint16_t)r1_time_utc_offset_get();
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_daily_hr_ring,r1_daily_hr_ring,r1_daily_hr_timestamp);
 uint32_t mode=r1_structured_log_mode_get();
 if(mode&2u)return nrf_log_frontend_std_1(0x001c0003,r1_daily_hr_sdk,r1_daily_hr_timestamp);
 return mode<<30;
}
#define VENEER(name,body) uint32_t name(void){return body();}
VENEER(r1_native_activity_cache_initialize,r1_daily_activity_refresh)
VENEER(r1_native_hr_cache_initialize,r1_daily_hr_refresh)
VENEER(r1_native_hrv_cache_initialize,r1_daily_hrv_refresh)
VENEER(r1_native_spo2_cache_initialize,r1_daily_spo2_refresh)
VENEER(r1_native_stress_cache_initialize,r1_daily_stress_refresh)
VENEER(r1_native_temperature_cache_initialize,r1_daily_temperature_refresh)
