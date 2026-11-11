#ifndef R1_NATIVE_HEALTH_OFFLINE_CONSUME_H
#define R1_NATIVE_HEALTH_OFFLINE_CONSUME_H
#include <stdint.h>
void r1_heart_rate_offline_queue_consume(uint32_t);
void r1_spo2_offline_queue_consume(uint32_t);
void r1_hrv_offline_queue_consume(uint32_t);
void r1_activity_offline_queue_consume(uint32_t);
uint32_t r1_heart_rate_offline_queue_empty(void);
uint32_t r1_spo2_offline_queue_empty(void);
uint32_t r1_hrv_offline_queue_empty(void);
uint32_t r1_activity_offline_queue_empty(void);
void r1_hr_sync_builder_reset(volatile uint8_t *);
void r1_spo2_sync_builder_reset(volatile uint8_t *);
void r1_hrv_sync_builder_reset(volatile uint8_t *);
void r1_activity_day_builder_reset(volatile uint8_t *);
#endif
