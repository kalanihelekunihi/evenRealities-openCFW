#include <stdint.h>
/* A C division by zero is undefined. Keep only the architectural operation
 * here so Cortex-M DIV_0_TRP continues to select zero or UsageFault. */
__attribute__((noinline)) uint32_t r1_arm_unsigned_divide_zero(uint32_t dividend)
{
 uint32_t quotient,zero=0;
 __asm__ volatile("udiv %0,%1,%2" : "=r"(quotient) : "r"(dividend),"r"(zero));
 return quotient;
}
/* Native stream period calculation divides the fixed 1024-tick clock by
 * its live byte divisor. Both callers route only divisor zero here. */
uint32_t r1_stream_zero_divisor_result(void)
{
 return r1_arm_unsigned_divide_zero(1024);
}
