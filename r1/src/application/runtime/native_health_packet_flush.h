#ifndef R1_NATIVE_HEALTH_PACKET_FLUSH_H
#define R1_NATIVE_HEALTH_PACKET_FLUSH_H
#include <stdint.h>
void r1_hr_sync_flush(volatile uint8_t *);
void r1_spo2_sync_flush(volatile uint8_t *);
void r1_hrv_sync_flush(volatile uint8_t *);
void r1_activity_day_packet_flush(volatile uint8_t *);
#endif
