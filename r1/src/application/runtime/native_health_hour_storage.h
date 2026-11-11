#ifndef R1_NATIVE_HEALTH_HOUR_STORAGE_H
#define R1_NATIVE_HEALTH_HOUR_STORAGE_H
#include <stdint.h>
void r1_health_hour_boundary_storage_orchestrator(uint32_t);
void r1_heart_rate_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
void r1_spo2_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
void r1_temperature_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
void r1_stress_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
void r1_activity_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
void r1_hrv_daily_cache_read(uint32_t,volatile uint8_t *,uint32_t);
uint32_t r1_stress_daily_cache_reset(uint32_t,uint32_t);
uint32_t r1_temperature_daily_cache_reset(uint32_t,uint32_t);
#endif
