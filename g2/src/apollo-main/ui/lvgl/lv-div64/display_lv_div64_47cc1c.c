/* Signed quotient used by Apollo Main's fixed-point Bezier Newton step.
 * Native entry 0x47cc1c; this C provider is bounded to quotient callers. */
#include <stdint.h>

int64_t audio_uart_lv_div64_47cc1c(int64_t numerator, int64_t denominator) {
    if (denominator == 0) return 0;
    const uint32_t negative = (numerator < 0) != (denominator < 0);
    uint64_t remaining = numerator < 0
        ? 0u - (uint64_t)numerator : (uint64_t)numerator;
    const uint64_t divisor = denominator < 0
        ? 0u - (uint64_t)denominator : (uint64_t)denominator;
    uint64_t quotient = 0;
    for (int bit = 63; bit >= 0; --bit) {
        if (divisor <= (remaining >> bit)) {
            remaining -= divisor << bit;
            quotient |= UINT64_C(1) << bit;
        }
    }
    if (negative) quotient = 0u - quotient;
    return (int64_t)quotient;
}
