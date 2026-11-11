/* Core-register Arm EABI boundaries around the canonical stock bit-pattern
 * providers. Do not replace the observed exceptional-value behavior with a
 * compiler-generated floating cast. */
#include <stdint.h>
extern uint32_t r1_log_double_to_float_bits(uint64_t);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint32_t r1_signed64_to_binary32_bits(uint64_t);

__attribute__((pcs("aapcs"))) float __aeabi_d2f(double value)
{
    union { double value; uint64_t bits; } input = { .value = value };
    union { float value; uint32_t bits; } output = {
        .bits = r1_log_double_to_float_bits(input.bits)
    };
    return output.value;
}

__attribute__((pcs("aapcs"))) double __aeabi_f2d(float value)
{
    union { float value; uint32_t bits; } input = { .value = value };
    union { double value; uint64_t bits; } output = {
        .bits = r1_binary32_to_binary64_bits(input.bits)
    };
    return output.value;
}

__attribute__((pcs("aapcs"))) float __aeabi_l2f(int64_t value)
{
    union { float value; uint32_t bits; } output = {
        .bits = r1_signed64_to_binary32_bits((uint64_t)value)
    };
    return output.value;
}
