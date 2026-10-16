#include <stdint.h>
extern uint64_t r1_binary64_square_root_bits(uint64_t);
extern uint32_t r1_native_errno_set(uint32_t);
/* Native 0x90e8c: encoded argument/result in R0/R1. D0 is an independent
 * incoming slot, not the argument or result. The recovered dependencies use
 * integer arithmetic and preserve it; direct verification checks this slot. */
static uint32_t native_nan(uint64_t bits)
{
 uint32_t magnitude=((uint32_t)(bits>>32)|((uint32_t)bits!=0))&0x7fffffffu;
 return (0x7ff00000u-magnitude)>>31;
}
uint64_t r1_native_sqrt_core_abi_bits(uint64_t input)
{
 uint64_t result=r1_binary64_square_root_bits(input);
 if(native_nan(result)&&!native_nan(input))r1_native_errno_set(1);
 return result;
}
