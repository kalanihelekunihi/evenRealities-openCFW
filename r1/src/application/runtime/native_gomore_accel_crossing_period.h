#ifndef R1_NATIVE_GOMORE_ACCEL_CROSSING_PERIOD_H
#define R1_NATIVE_GOMORE_ACCEL_CROSSING_PERIOD_H
#include <stdint.h>
/* Stock 0x56f94 boundary: native C candidate; incoming float seed is unused. */
uint32_t r1_gomore_accel_crossing_period_native(float,uint32_t,uint32_t,uint32_t,uint32_t);
int32_t r1_gomore_accel_u8_compare_native(const void *,const void *);
#endif
