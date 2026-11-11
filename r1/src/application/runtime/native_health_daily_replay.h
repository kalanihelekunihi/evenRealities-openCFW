#ifndef R1_NATIVE_HEALTH_DAILY_REPLAY_H
#define R1_NATIVE_HEALTH_DAILY_REPLAY_H
#include <flashdb.h>
#include <stdint.h>
bool r1_health_daily_record_replay(fdb_tsl_t,void *);
void r1_heart_rate_daily_cache_write(uint32_t,const volatile uint8_t *);
void r1_spo2_daily_cache_write(uint32_t,const volatile uint8_t *);
void r1_temperature_daily_cache_write(uint32_t,const volatile uint8_t *);
void r1_stress_daily_cache_write(uint32_t,const volatile uint8_t *);
void r1_activity_daily_cache_write(uint32_t,const volatile uint8_t *);
void r1_hrv_daily_cache_write(uint32_t,const volatile uint8_t *);
volatile uint8_t *r1_stress_daily_cache_accessor(void);
volatile uint8_t *r1_temperature_daily_cache_accessor(void);
#endif
