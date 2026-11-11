/* SPDX-License-Identifier: MIT
 * Native image-B GSC reciprocal at 0x1000c9e0: one C-SKY frecips. The
 * CK804EF hard-float ABI passes and returns the scalar in fr0. The inline
 * asm pins that instruction, so the hardware reciprocal (its rounding and
 * its handling of 0, infinities, NaN and denormals) is kept, rather than
 * a division the compiler may lower differently. ("v" is the FPU register
 * constraint of csky-abiv2-gcc 6.3.)
 */

float gx8002_image_b_native_reciprocal_f32(float x)
{
    float result;
    __asm__("frecips %0, %1" : "=v"(result) : "v"(x));
    return result;
}
