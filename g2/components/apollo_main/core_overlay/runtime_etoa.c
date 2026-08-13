/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2014-2019 Marco Paland
 *
 * Bounded source recovery of mpaland/printf _etoa from the G2 2.2.6.10
 * firmware. Semantics derive from upstream commit
 * d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e.
 */

typedef __UINT64_TYPE__ open_cfw_runtime_etoa_u64;

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

#ifndef OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#define OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_RUNTIME_FLOAT_ABI \
    __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_RUNTIME_FLOAT_ABI
#endif
#endif

enum {
    OPEN_CFW_RUNTIME_ETOA_ZERO_PAD = 1U << 0U,
    OPEN_CFW_RUNTIME_ETOA_LEFT = 1U << 1U,
    OPEN_CFW_RUNTIME_ETOA_PLUS = 1U << 2U,
    OPEN_CFW_RUNTIME_ETOA_UPPER = 1U << 5U,
    OPEN_CFW_RUNTIME_ETOA_PRECISION = 1U << 10U,
    OPEN_CFW_RUNTIME_ETOA_ADAPT_EXP = 1U << 11U,
    OPEN_CFW_RUNTIME_ETOA_DEFAULT_PRECISION = 6U
};

#ifndef OPEN_CFW_RUNTIME_ETOA_FTOA
OPEN_CFW_RUNTIME_FLOAT_ABI
unsigned int open_cfw_runtime_ftoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
);
#define OPEN_CFW_RUNTIME_ETOA_FTOA( \
    output, buffer, index, maximum_length, value, precision, width, flags \
) \
    open_cfw_runtime_ftoa( \
        (output), (buffer), (index), (maximum_length), \
        (value), (precision), (width), (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_ETOA_NTOA_LONG
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
);
#define OPEN_CFW_RUNTIME_ETOA_NTOA_LONG( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    value, \
    negative, \
    base, \
    precision, \
    width, \
    flags \
) \
    open_cfw_runtime_ntoa_long( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (value), \
        (negative), \
        (base), \
        (precision), \
        (width), \
        (flags) \
    )
#endif

#if defined(__arm__) && defined(__clang__)
#define OPEN_CFW_RUNTIME_ETOA_FP64 \
    __attribute__((target("fp64")))
#else
#define OPEN_CFW_RUNTIME_ETOA_FP64
#endif

__attribute__((used, noinline))
OPEN_CFW_RUNTIME_ETOA_FP64
OPEN_CFW_RUNTIME_FLOAT_ABI
unsigned int open_cfw_runtime_etoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    unsigned int index,
    unsigned int maximum_length,
    double value,
    unsigned int precision,
    unsigned int width,
    unsigned int flags
)
{
    union {
        open_cfw_runtime_etoa_u64 bits;
        double floating;
    } conversion;
    _Bool negative;
    int exponent_two;
    int exponent_decimal;
    double z;
    double z_squared;
    unsigned int exponent_width;
    unsigned int floating_width;
    unsigned int start_index;

    if (
        value != value
        || value > __DBL_MAX__
        || value < -__DBL_MAX__
    ) {
        return OPEN_CFW_RUNTIME_ETOA_FTOA(
            output,
            buffer,
            index,
            maximum_length,
            value,
            precision,
            width,
            flags
        );
    }

    negative = value < 0.0;
    if (negative) {
        value = -value;
    }

    if ((flags & OPEN_CFW_RUNTIME_ETOA_PRECISION) == 0U) {
        precision = OPEN_CFW_RUNTIME_ETOA_DEFAULT_PRECISION;
    }

    conversion.floating = value;
    exponent_two =
        (int)((conversion.bits >> 52U) & 0x07FFU) - 1023;
    conversion.bits = (
        conversion.bits & ((((open_cfw_runtime_etoa_u64)1U) << 52U) - 1U)
    ) | (((open_cfw_runtime_etoa_u64)1023U) << 52U);
    exponent_decimal = (int)(
        0.1760912590558
        + exponent_two * 0.301029995663981
        + (conversion.floating - 1.5) * 0.289529654602168
    );
    exponent_two = (int)(
        exponent_decimal * 3.321928094887362 + 0.5
    );
    z = (
        exponent_decimal * 2.302585092994046
        - exponent_two * 0.6931471805599453
    );
    z_squared = z * z;
    conversion.bits =
        (open_cfw_runtime_etoa_u64)(exponent_two + 1023) << 52U;
    conversion.floating *= (
        1.0
        + 2.0 * z
            / (
                2.0 - z
                + (
                    z_squared
                    / (
                        6.0
                        + (
                            z_squared
                            / (10.0 + z_squared / 14.0)
                        )
                    )
                )
            )
    );

    if (value < conversion.floating) {
        exponent_decimal -= 1;
        conversion.floating /= 10.0;
    }

    exponent_width = (
        exponent_decimal < 100 && exponent_decimal > -100
        ? 4U
        : 5U
    );

    if ((flags & OPEN_CFW_RUNTIME_ETOA_ADAPT_EXP) != 0U) {
        if (value >= 1e-4 && value < 1e6) {
            if ((int)precision > exponent_decimal) {
                precision = (unsigned int)(
                    (int)precision - exponent_decimal - 1
                );
            }
            else {
                precision = 0U;
            }
            flags |= OPEN_CFW_RUNTIME_ETOA_PRECISION;
            exponent_width = 0U;
            exponent_decimal = 0;
        }
        else if (
            precision > 0U
            && (flags & OPEN_CFW_RUNTIME_ETOA_PRECISION) != 0U
        ) {
            precision -= 1U;
        }
    }

    floating_width = width;
    if (width > exponent_width) {
        floating_width -= exponent_width;
    }
    else {
        floating_width = 0U;
    }
    if (
        (flags & OPEN_CFW_RUNTIME_ETOA_LEFT) != 0U
        && exponent_width != 0U
    ) {
        floating_width = 0U;
    }

    if (exponent_decimal != 0) {
        value /= conversion.floating;
    }

    start_index = index;
    index = OPEN_CFW_RUNTIME_ETOA_FTOA(
        output,
        buffer,
        index,
        maximum_length,
        negative ? -value : value,
        precision,
        floating_width,
        flags & ~OPEN_CFW_RUNTIME_ETOA_ADAPT_EXP
    );

    if (exponent_width != 0U) {
        output(
            (flags & OPEN_CFW_RUNTIME_ETOA_UPPER) != 0U ? 'E' : 'e',
            buffer,
            index,
            maximum_length
        );
        index += 1U;
        index = OPEN_CFW_RUNTIME_ETOA_NTOA_LONG(
            output,
            buffer,
            index,
            maximum_length,
            exponent_decimal < 0
                ? (unsigned int)-exponent_decimal
                : (unsigned int)exponent_decimal,
            exponent_decimal < 0,
            10U,
            0U,
            exponent_width - 1U,
            OPEN_CFW_RUNTIME_ETOA_ZERO_PAD
                | OPEN_CFW_RUNTIME_ETOA_PLUS
        );
        if ((flags & OPEN_CFW_RUNTIME_ETOA_LEFT) != 0U) {
            while (index - start_index < width) {
                output(' ', buffer, index, maximum_length);
                index += 1U;
            }
        }
    }
    return index;
}

#undef OPEN_CFW_RUNTIME_ETOA_FP64
#undef OPEN_CFW_RUNTIME_ETOA_FTOA
#undef OPEN_CFW_RUNTIME_ETOA_NTOA_LONG
