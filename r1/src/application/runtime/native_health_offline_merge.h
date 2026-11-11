#ifndef R1_NATIVE_HEALTH_OFFLINE_MERGE_H
#define R1_NATIVE_HEALTH_OFFLINE_MERGE_H
#include <stdint.h>
void r1_heart_rate_offline_queue_merge(volatile uint8_t *);
void r1_spo2_offline_queue_merge(volatile uint8_t *);
void r1_hrv_offline_queue_merge(volatile uint8_t *);
void r1_activity_offline_queue_merge(volatile uint8_t *);
#endif
