/* SPDX-License-Identifier: MIT
 * Stage-1 software unsigned quotient 0x1000013c and remainder 0x10000180.
 * These translate the retained shift/subtract bodies, including their
 * defined zero-divisor termination, rather than substituting CPU DIVU.
 */
#include <stdint.h>

uint32_t gx8002_uart_stage1_udiv(uint32_t numerator, uint32_t denominator)
{
    uint32_t mask = 1;
    if (denominator < numerator && (int32_t)denominator >= 0) {
        unsigned remaining = 32;
        for (;;) {
            denominator <<= 1;
            mask <<= 1;
            if (numerator <= denominator) {
                if (mask == 0) return 0;
                break;
            }
            if (--remaining == 0) return 0;
            if ((int32_t)denominator < 0) break;
        }
    }
    uint32_t quotient = 0;
    do {
        if (denominator <= numerator) {
            numerator -= denominator;
            quotient |= mask;
        }
        mask >>= 1;
        denominator >>= 1;
    } while (mask != 0);
    return quotient;
}

uint32_t gx8002_uart_stage1_umod(uint32_t numerator, uint32_t denominator)
{
    uint32_t mask = 0;
    if (denominator < numerator && (int32_t)denominator >= 0) {
        unsigned remaining = 32;
        mask = 1;
        for (;;) {
            denominator <<= 1;
            mask <<= 1;
            if (numerator <= denominator) {
                if (mask == 0) return numerator;
                break;
            }
            if (--remaining == 0) return numerator;
            if ((int32_t)denominator < 0) break;
        }
    }
    do {
        mask >>= 1;
        if (denominator <= numerator) numerator -= denominator;
        denominator >>= 1;
    } while (mask != 0);
    return numerator;
}
