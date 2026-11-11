#ifndef R1_NATIVE_HEALTH_PROFILE_H
#define R1_NATIVE_HEALTH_PROFILE_H
#include <stdint.h>
uint32_t r1_record12_validate(const volatile uint8_t *record);
uint32_t r1_health_profile_features(const volatile uint8_t *record, volatile float *out);
/* Seed words preserve the stock scratch contents when the cached class rejects its size. */
uint64_t r1_kv_health_get(void *out, uint32_t seed0, uint32_t seed1, uint32_t seed2);
uint64_t r1_health_lifecycle_profile_native(void *out, uint32_t seed0, uint32_t seed1, uint32_t seed2);
#endif
