#ifndef R1_NATIVE_GOMORE_ACCEL_RING_SCORE_H
#define R1_NATIVE_GOMORE_ACCEL_RING_SCORE_H
#include <stdint.h>
/* Stock 0x56a0c: fixed six-channel model, sorted final three summed channels. */
uint32_t r1_gomore_accel_ring_score_native(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,
                                         uint32_t,uint32_t,uint32_t,uint32_t);
#endif
