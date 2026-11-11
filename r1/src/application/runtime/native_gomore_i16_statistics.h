#ifndef R1_NATIVE_GOMORE_I16_STATISTICS_H
#define R1_NATIVE_GOMORE_I16_STATISTICS_H
#include <stdint.h>
uint32_t r1_gomore_i16_mean_native(uint32_t,uint32_t);
uint32_t r1_gomore_i16_range_native(uint32_t,uint32_t);
uint32_t r1_gomore_i16_mean_difference_native(uint32_t,uint32_t);
/* Shared wrapped variance arithmetic; no independent stock-function anchor. */
uint32_t r1_gomore_i16_variance_bits(uint32_t,uint32_t,uint32_t);
float r1_gomore_i16_deviation_native(uint32_t,uint32_t,uint32_t);
#endif
