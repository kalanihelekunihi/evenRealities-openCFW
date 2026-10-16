#include <stdint.h>
extern uint64_t r1_binary64_square_root_bits(uint64_t);
/* Authenticated native errno pointer0x3bca4 names this four-byte SRAM cell.
 * Verification links the cell at0x20007dbc. Its cold initialization and final
 * whole-image placement remain separate gates; callers supply existing state. */
__attribute__((section(".r1.runtime.errno"),used))
volatile uint32_t r1_native_math_errno;
uint32_t r1_native_errno_set(uint32_t value)
{
    r1_native_math_errno=value;
    return value;
}
static uint32_t native_nan64(uint64_t bits)
{
    uint32_t magnitude=((uint32_t)(bits>>32)&0x7fffffffu)|((uint32_t)bits!=0);
    return (0x7ff00000u-magnitude)>>31;
}
double r1_native_sqrt(double x)
{
    union { double value; uint64_t bits; } input={.value=x},result;
    result.bits=r1_binary64_square_root_bits(input.bits);
    if (native_nan64(result.bits) && !native_nan64(input.bits)) r1_native_errno_set(1);
    return result.value;
}
float r1_native_sqrtf(float x)
{
    union { float value; uint32_t bits; } input={.value=x},result;
    /* Preserve the authenticated VFP instruction and FPSCR exception behavior. */
    __asm__ volatile("vsqrt.f32 %0,%1" : "=t"(result.value) : "t"(x));
    uint32_t result_nan=(0x7f800000u-(result.bits&0x7fffffffu))>>31;
    uint32_t input_nan=(0x7f800000u-(input.bits&0x7fffffffu))>>31;
    if (result_nan && !input_nan) r1_native_errno_set(1);
    return result.value;
}
