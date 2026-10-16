#include <stdint.h>
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_add_bits(uint64_t,uint64_t);
/* Native 0x3b40c: hard-float x/result in d0, coefficients/count in r0/r1.
 * Coefficients are ascending powers. Arithmetic remains the recovered raw-bit
 * providers; host double operators would change exceptional/subnormal rules.
 * Count zero, unbounded counts, invalid pointers and private stack aliases
 * remain explicit evidence gates; no synthetic result is supplied for them. */
double r1_native_polynomial(double x,const uint64_t *coefficients,uint32_t count)
{
    union { double value; uint64_t bits; } argument={.value=x},result;
    uint32_t index=count-1u;
    result.bits=coefficients[index];
    while(index) {
        result.bits=r1_format_double_multiply_bits(result.bits,argument.bits);
        result.bits=r1_format_double_add_bits(result.bits,coefficients[--index]);
    }
    return result.value;
}
