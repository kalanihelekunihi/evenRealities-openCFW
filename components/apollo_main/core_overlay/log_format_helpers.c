/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the non-floating helper cluster used by the G2
 * 2.2.6.10 application-wide logging formatter at 0x00473036.
 */

typedef unsigned char open_cfw_log_u8;
typedef unsigned int open_cfw_log_u32;

static __attribute__((always_inline)) inline void
open_cfw_log_divmod_u64_by_10(
    open_cfw_log_u32 low,
    open_cfw_log_u32 high,
    open_cfw_log_u32 *quotient_low,
    open_cfw_log_u32 *quotient_high,
    open_cfw_log_u32 *remainder
)
{
    open_cfw_log_u32 output_low = 0U;
    open_cfw_log_u32 output_high = 0U;
    open_cfw_log_u32 residual = 0U;
    open_cfw_log_u32 index;

    /*
     * Bitwise long division keeps the freestanding Cortex-M build independent
     * of compiler-provided 64-bit division runtime functions.
     */
    for (index = 0U; index < 64U; index += 1U) {
        open_cfw_log_u32 incoming = high >> 31U;

        high = (high << 1U) | (low >> 31U);
        low <<= 1U;
        output_high = (output_high << 1U) | (output_low >> 31U);
        output_low <<= 1U;
        residual = (residual << 1U) | incoming;
        if (residual >= 10U) {
            residual -= 10U;
            output_low |= 1U;
        }
    }
    *quotient_low = output_low;
    *quotient_high = output_high;
    *remainder = residual;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_decimal_digits(
    unsigned int low,
    unsigned int high
)
{
    unsigned int count = 0U;

    do {
        unsigned int quotient_low;
        unsigned int quotient_high;
        unsigned int remainder;

        open_cfw_log_divmod_u64_by_10(
            low,
            high,
            &quotient_low,
            &quotient_high,
            &remainder
        );
        low = quotient_low;
        high = quotient_high;
        count += 1U;
    } while ((low != 0U) || (high != 0U));
    return count;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_signed_decimal_digits(
    unsigned int low,
    unsigned int high
)
{
    if ((high & 0x80000000U) != 0U) {
        unsigned int borrow = low != 0U ? 1U : 0U;

        low = 0U - low;
        high = (0U - high) - borrow;
    }
    return open_cfw_log_decimal_digits(low, high);
}

__attribute__((used, noinline))
unsigned int open_cfw_log_hex_digits(
    unsigned int low,
    unsigned int high
)
{
    unsigned int count = 0U;

    do {
        low = (low >> 4U) | (high << 28U);
        high >>= 4U;
        count += 1U;
    } while ((low != 0U) || (high != 0U));
    return count;
}

__attribute__((used, noinline))
int open_cfw_log_parse_integer(
    const unsigned char *text,
    unsigned int *consumed
)
{
    unsigned int negative = 0U;
    unsigned int count = 0U;
    unsigned int value = 0U;

    if (*text == (unsigned char)'-') {
        negative = 1U;
        text += 1;
        count = 1U;
    }
    while ((unsigned int)(*text - (unsigned char)'0') < 10U) {
        value = (value * 10U) + (unsigned int)(*text - (unsigned char)'0');
        text += 1;
        count += 1U;
    }
    if (consumed != (unsigned int *)0) {
        *consumed = count;
    }
    return (int)(negative != 0U ? 0U - value : value);
}

__attribute__((used, noinline))
unsigned int open_cfw_log_decimal_write(
    unsigned int low,
    unsigned int high,
    char *destination
)
{
    char reversed[20];
    unsigned int count = 0U;

    do {
        unsigned int quotient_low;
        unsigned int quotient_high;
        unsigned int remainder;

        open_cfw_log_divmod_u64_by_10(
            low,
            high,
            &quotient_low,
            &quotient_high,
            &remainder
        );
        reversed[count] = (char)('0' + remainder);
        count += 1U;
        low = quotient_low;
        high = quotient_high;
    } while ((low != 0U) || (high != 0U));

    if (destination != (char *)0) {
        unsigned int index;

        for (index = 0U; index < count; index += 1U) {
            destination[index] = reversed[count - index - 1U];
        }
        destination[count] = '\0';
    }
    return count;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_hex_write(
    unsigned int low,
    unsigned int high,
    char *destination,
    unsigned int lowercase
)
{
    char reversed[16];
    unsigned int count = 0U;

    do {
        unsigned int nibble = low & 0xFU;

        reversed[count] = (char)(
            nibble < 10U
                ? (unsigned int)'0' + nibble
                : (unsigned int)(lowercase != 0U ? 'a' : 'A')
                    + nibble - 10U
        );
        count += 1U;
        low = (low >> 4U) | (high << 28U);
        high >>= 4U;
    } while ((low != 0U) || (high != 0U));

    if (destination != (char *)0) {
        unsigned int index;

        for (index = 0U; index < count; index += 1U) {
            destination[index] = reversed[count - index - 1U];
        }
        destination[count] = '\0';
    }
    return count;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_string_length(const char *text)
{
    unsigned int length = 0U;

    if (text != (const char *)0) {
        while (*text != '\0') {
            text += 1;
            length += 1U;
        }
    }
    return length;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_padding_write(
    char *destination,
    unsigned int fill,
    int count
)
{
    unsigned int written = 0U;

    while (count > 0) {
        if (destination != (char *)0) {
            *destination = (char)fill;
            destination += 1;
        }
        written += 1U;
        count -= 1;
    }
    return written;
}
