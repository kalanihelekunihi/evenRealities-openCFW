/* SPDX-License-Identifier: MIT
 * Numeric formatter at stage-2 0x1000691c. Source arithmetic follows its
 * sign, alternate form, precision, width, and reverse-digit control flow.
 */
#include <stdint.h>

enum { N_ZERO = 1, N_SIGNED = 2, N_PLUS = 4, N_SPACE = 8,
       N_LEFT = 16, N_LOWER = 32, N_ALT = 64 };

static uint64_t quotient_small(uint64_t value, uint32_t base, uint32_t *remainder)
{
    uint64_t result = 0;
    uint32_t rest = 0;
    for (int bit = 63; bit >= 0; --bit) {
        rest = (rest << 1) | (uint32_t)((value >> bit) & 1u);
        if (rest >= base) { rest -= base; result |= UINT64_C(1) << bit; }
    }
    *remainder = rest;
    return result;
}

uint32_t gx8002_uart_stage2_divide_65e4(uint64_t *value, uint32_t divisor)
{
    if (divisor == 0) {
        uint32_t exceptional;
        const uint32_t numerator = (uint32_t)*value;
        __asm__ volatile("divu %0, %1, %2" : "=r"(exceptional)
                         : "r"(numerator), "r"(divisor) : "cc");
        *value = exceptional;
        return 0;
    }
    uint32_t remainder;
    *value = quotient_small(*value, divisor, &remainder);
    return remainder;
}

char *gx8002_uart_stage2_decimal_reverse_6774(char *out,
    uint32_t low, uint32_t high)
{
    uint64_t number = ((uint64_t)high << 32) | low;
    do {
        const uint32_t digit = gx8002_uart_stage2_divide_65e4(&number, 10u);
        *out++ = (char)('0' + digit);
    } while (number != 0);
    return out;
}

char *gx8002_uart_stage2_format_number_691c(char *out,
    uint32_t low, uint32_t high, uint32_t base, int32_t width,
    int32_t precision, uint32_t flags)
{
    uint64_t number = ((uint64_t)high << 32) | low;
    char sign = 0;
    if (flags & N_LEFT) flags &= ~N_ZERO;
    if (flags & N_SIGNED) {
        if ((int32_t)high < 0) {
            sign = '-';
            number = ~number + 1u;
        } else if (flags & N_PLUS) sign = '+';
        else if (flags & N_SPACE) sign = ' ';
    }
    if (sign) --width;
    if ((flags & N_ALT) && base != 10u)
        width -= base == 16u ? 2 : 1;

    char digits[69];
    uint32_t count = 0;
    const char *const alphabet = (flags & N_LOWER)
        ? "0123456789abcdef" : "0123456789ABCDEF";
    if (base == 10u) {
        count = (uint32_t)(gx8002_uart_stage2_decimal_reverse_6774(
            digits, (uint32_t)number, (uint32_t)(number >> 32)) - digits);
    } else {
        do {
            uint32_t digit;
            number = quotient_small(number, base, &digit);
            digits[count++] = alphabet[digit];
        } while (number != 0 && count < sizeof(digits));
    }
    int32_t digit_width = precision > (int32_t)count ? precision : (int32_t)count;
    width -= digit_width;
    if (!(flags & (N_LEFT | N_ZERO)))
        while (width-- > 0) *out++ = ' ';
    if (sign) *out++ = sign;
    if ((flags & N_ALT) && base != 10u) {
        *out++ = '0';
        if (base == 16u) *out++ = (flags & N_LOWER) ? 'x' : 'X';
    }
    if (!(flags & N_LEFT))
        while (width-- > 0) *out++ = (flags & N_ZERO) ? '0' : ' ';
    while (digit_width-- > (int32_t)count) *out++ = '0';
    while (count != 0) *out++ = digits[--count];
    if (flags & N_LEFT) while (width-- > 0) *out++ = ' ';
    return out;
}
