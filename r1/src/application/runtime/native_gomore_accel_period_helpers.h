#ifndef R1_NATIVE_GOMORE_ACCEL_PERIOD_HELPERS_H
#define R1_NATIVE_GOMORE_ACCEL_PERIOD_HELPERS_H
#include <stdint.h>
uint32_t r1_gomore_accel_iir4_native(uint32_t,uint32_t,uint32_t,uint32_t);
/* S0 target, S1 unused, S2/S3 shapes; R0..R3 point to interval/pair/flag/estimate. */
uint32_t r1_gomore_accel_transition_native(float,float,float,float,uint32_t,uint32_t,uint32_t,uint32_t);
#endif
