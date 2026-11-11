#ifndef R1_NATIVE_GOMORE_ACCEL_AUTOCORRELATION_H
#define R1_NATIVE_GOMORE_ACCEL_AUTOCORRELATION_H
#include <stdint.h>
#include <stddef.h>
/* Stock 0x5c5f0 / 0x56d78. Kernel preserves R0/R1; enabled wrapper returns fourth/fifth pointers. */
uint64_t r1_gomore_accel_autocorrelation_native(const uint16_t *,float *,float *,float *,float *,float *,uintptr_t,uintptr_t);
uint64_t r1_gomore_accel_autocorrelation_wrapper_native(uint32_t,const uint16_t *,float *,float *,float *,float *,float *,uintptr_t,uintptr_t);
#endif
