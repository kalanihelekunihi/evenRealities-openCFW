#ifndef R1_NATIVE_GOMORE_ACCEL_CLASS_HELPERS_H
#define R1_NATIVE_GOMORE_ACCEL_CLASS_HELPERS_H
#include <stdint.h>
float r1_gomore_accel_nonzero_mean8_native(uint32_t);
uint32_t r1_gomore_accel_hysteresis_count_native(uint32_t,uint32_t);
uint32_t r1_gomore_accel_linear_classify_native(float,float,float,uint32_t);
#endif
