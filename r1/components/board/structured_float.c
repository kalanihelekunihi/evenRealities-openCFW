#include <stdint.h>

/* Stock Arm runtime 0x28078. This is a bit-pattern rounding primitive. */
uint32_t r1_log_round_float_bits(uint32_t value, uint32_t remainder)
{
    if (remainder & UINT32_C(0x80000000)) {
        ++value;
        if ((remainder & UINT32_C(0x7fffffff)) == 0)
            value &= ~UINT32_C(1);
    }
    return value;
}

/* Stock 0x27f6c: intentionally preserve its exponent arithmetic, zero-sign
 * loss and missing IEEE exceptional-value handling rather than use a C cast. */
uint32_t r1_log_double_to_float_bits(uint64_t bits)
{
    uint32_t low = (uint32_t)bits;
    uint32_t high = (uint32_t)(bits >> 32);
    uint32_t magnitude = high & UINT32_C(0x7fffffff);
    int32_t exponent = (int32_t)(magnitude >> 20) - 896;
    if ((low == 0 && magnitude == 0) || exponent <= 0)
        return 0;
    uint32_t value = (low >> 29) | ((magnitude & UINT32_C(0xfffff)) << 3);
    value += high & UINT32_C(0x80000000);
    value += (uint32_t)exponent << 23;
    return r1_log_round_float_bits(value, low << 3);
}
