#ifndef R1_NATIVE_GOMORE_ACCEL_RING_PREDICATES_H
#define R1_NATIVE_GOMORE_ACCEL_RING_PREDICATES_H
#include <stdint.h>
uint32_t r1_gomore_accel_band_count_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_accel_recent_mean3_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_accel_activity_gate_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t r1_gomore_accel_recent_decision_native(uint32_t,uint32_t);
#endif
