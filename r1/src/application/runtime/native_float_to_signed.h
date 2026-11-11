#ifndef R1_NATIVE_FLOAT_TO_SIGNED_H
#define R1_NATIVE_FLOAT_TO_SIGNED_H
#include <stdint.h>
/* ARM VCVT.s32.f32 result bits and cumulative FPSCR effects, with round-to-zero. */
uint32_t r1_native_float_to_signed32(float);
#endif
