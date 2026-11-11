#ifndef R1_NATIVE_CRASH_RECOVERY_H
#define R1_NATIVE_CRASH_RECOVERY_H
#include <stdint.h>
uint32_t r1_health_crash_provider_blob_clear(void);
uint32_t r1_health_crash_provider_blob_accessor(volatile uint16_t *);
uint32_t r1_health_crash_record_magic_probe(void);
uint32_t r1_health_crash_record_validator(void);
uint32_t r1_health_crash_time_clear(void);
uint32_t r1_health_crash_time_accessor(volatile uint32_t *,volatile uint16_t *,volatile uint8_t *);
uint32_t r1_health_crash_snapshot_clear(void);
uint32_t r1_health_crash_snapshot_accessor(volatile uint8_t *);
void r1_health_crash_snapshot_restore(void);
#endif
