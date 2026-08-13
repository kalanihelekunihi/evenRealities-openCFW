/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacements for the G2 2.2.6.10 mpaland/printf integer
 * conversion helpers:
 *   0x0048320A...0x0048329B  _ntoa_long
 *   0x0048329C...0x0048334D  _ntoa_long_long
 *
 * The conversion semantics derive from Marco Paland's printf implementation
 * at commit d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e. The resulting reverse
 * digit buffer is forwarded to the separately recoverable _ntoa_format.
 *
 * Copyright (c) 2014-2019 Marco Paland
 */

typedef __UINT64_TYPE__ open_cfw_runtime_ntoa_u64;
#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

enum {
    OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE = 32U,
    OPEN_CFW_RUNTIME_NTOA_FLAG_HASH = 1U << 4U,
    OPEN_CFW_RUNTIME_NTOA_FLAG_UPPER = 1U << 5U,
    OPEN_CFW_RUNTIME_NTOA_FLAG_PRECISION = 1U << 10U
};

#ifndef OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
#define OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
struct open_cfw_aeabi_divmod_result {
    unsigned int quotient_low;
    unsigned int quotient_high;
    unsigned int remainder_low;
    unsigned int remainder_high;
};
#endif

#ifndef OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64
void open_cfw_aeabi_uldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
);
#define OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(value, base, result) \
    open_cfw_aeabi_uldivmod_core( \
        (unsigned int)(value), \
        (unsigned int)((value) >> 32U), \
        (unsigned int)(base), \
        (unsigned int)((base) >> 32U), \
        (result) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_NTOA_FORMAT
unsigned int open_cfw_runtime_ntoa_format(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    char *digits,
    unsigned int digit_count,
    _Bool negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
);
#define OPEN_CFW_RUNTIME_NTOA_FORMAT( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    digits, \
    digit_count, \
    negative, \
    base, \
    precision, \
    width, \
    flags \
) \
    open_cfw_runtime_ntoa_format( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (digits), \
        (digit_count), \
        (negative), \
        (base), \
        (precision), \
        (width), \
        (flags) \
    )
#endif

static __attribute__((always_inline)) inline
open_cfw_runtime_ntoa_u64 open_cfw_runtime_ntoa_join(
    unsigned int low,
    unsigned int high
)
{
    return (
        ((open_cfw_runtime_ntoa_u64)high << 32U)
        | (open_cfw_runtime_ntoa_u64)low
    );
}

static __attribute__((always_inline)) inline char
open_cfw_runtime_ntoa_digit(unsigned int digit, unsigned int flags)
{
    if (digit < 10U) {
        return (char)('0' + digit);
    }
    return (char)(
        (
            (flags & OPEN_CFW_RUNTIME_NTOA_FLAG_UPPER) != 0U
            ? 'A'
            : 'a'
        )
        + digit
        - 10U
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_ntoa_long(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    unsigned int value,
    _Bool negative,
    unsigned int base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    char digits[OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE];
    unsigned int digit_count = 0U;

    if (value == 0U) {
        flags &= ~OPEN_CFW_RUNTIME_NTOA_FLAG_HASH;
    }

    if (
        (flags & OPEN_CFW_RUNTIME_NTOA_FLAG_PRECISION) == 0U
        || value != 0U
    ) {
        do {
            unsigned int digit = value % base;

            digits[digit_count++] =
                open_cfw_runtime_ntoa_digit(digit, flags);
            value /= base;
        } while (
            value != 0U
            && digit_count < OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE
        );
    }

    return OPEN_CFW_RUNTIME_NTOA_FORMAT(
        output,
        buffer,
        index,
        maximum_length,
        digits,
        digit_count,
        negative,
        base,
        precision,
        width,
        flags
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_runtime_ntoa_long_long(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    open_cfw_runtime_ntoa_u64 value,
    _Bool negative,
    open_cfw_runtime_ntoa_u64 base,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    char digits[OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE];
    unsigned int digit_count = 0U;

    if (value == 0U) {
        flags &= ~OPEN_CFW_RUNTIME_NTOA_FLAG_HASH;
    }

    if (
        (flags & OPEN_CFW_RUNTIME_NTOA_FLAG_PRECISION) == 0U
        || value != 0U
    ) {
        do {
            struct open_cfw_aeabi_divmod_result division;

            OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(
                value,
                base,
                &division
            );
            digits[digit_count++] = open_cfw_runtime_ntoa_digit(
                division.remainder_low,
                flags
            );
            value = open_cfw_runtime_ntoa_join(
                division.quotient_low,
                division.quotient_high
            );
        } while (
            value != 0U
            && digit_count < OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE
        );
    }

    return OPEN_CFW_RUNTIME_NTOA_FORMAT(
        output,
        buffer,
        index,
        maximum_length,
        digits,
        digit_count,
        negative,
        (unsigned int)base,
        precision,
        width,
        flags
    );
}

#undef OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64
#undef OPEN_CFW_RUNTIME_NTOA_FORMAT
