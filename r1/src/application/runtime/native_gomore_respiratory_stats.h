#ifndef R1_NATIVE_GOMORE_RESPIRATORY_STATS_H
#define R1_NATIVE_GOMORE_RESPIRATORY_STATS_H
#include <stdint.h>
uint32_t r1_gomore_encoded_count_native(volatile const void *values,uint32_t length);
uint32_t r1_gomore_argmax_native(volatile const float *values,uint32_t length);
uint32_t r1_gomore_threshold5_native(float threshold,volatile const float *values,volatile const float *weights,volatile float *output);
#endif
