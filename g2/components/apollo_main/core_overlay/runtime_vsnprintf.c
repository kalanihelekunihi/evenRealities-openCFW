/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2014-2019 Marco Paland
 *
 * Source recovery of the G2 2.2.6.10 mpaland/printf _vsnprintf core at
 * 0x00483960...0x00483FCB. The ordinary formatter behavior derives from
 * mpaland/printf commit d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e.
 *
 * The firmware enables binary, long-long, floating-point, exponential, and
 * ptrdiff formatting. It additionally implements the Linux-style %PV
 * recursive descriptor extension. The same stock branch also accepts %pV.
 */

typedef __INT32_TYPE__ open_cfw_runtime_vsnprintf_s32;
typedef __UINT32_TYPE__ open_cfw_runtime_vsnprintf_u32;
typedef __INT64_TYPE__ open_cfw_runtime_vsnprintf_s64;
typedef __UINT64_TYPE__ open_cfw_runtime_vsnprintf_u64;
typedef __UINTPTR_TYPE__ open_cfw_runtime_vsnprintf_uintptr;

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char character,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length
);
#endif

#ifndef OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#define OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_RUNTIME_FLOAT_ABI __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_RUNTIME_FLOAT_ABI
#endif
#endif

enum {
    OPEN_CFW_RUNTIME_VSNPRINTF_ZERO_PAD = 1U << 0U,
    OPEN_CFW_RUNTIME_VSNPRINTF_LEFT = 1U << 1U,
    OPEN_CFW_RUNTIME_VSNPRINTF_PLUS = 1U << 2U,
    OPEN_CFW_RUNTIME_VSNPRINTF_SPACE = 1U << 3U,
    OPEN_CFW_RUNTIME_VSNPRINTF_HASH = 1U << 4U,
    OPEN_CFW_RUNTIME_VSNPRINTF_UPPER = 1U << 5U,
    OPEN_CFW_RUNTIME_VSNPRINTF_CHAR = 1U << 6U,
    OPEN_CFW_RUNTIME_VSNPRINTF_SHORT = 1U << 7U,
    OPEN_CFW_RUNTIME_VSNPRINTF_LONG = 1U << 8U,
    OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG = 1U << 9U,
    OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION = 1U << 10U,
    OPEN_CFW_RUNTIME_VSNPRINTF_ADAPT_EXP = 1U << 11U
};

struct open_cfw_runtime_vsnprintf_recursive {
    const unsigned char *format;
    __builtin_va_list *arguments;
};

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT
void open_cfw_runtime_vsnprintf_noop_output(
    char character,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length
) __asm__("open_cfw_runtime_noop_output");
#define OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT \
    open_cfw_runtime_vsnprintf_noop_output
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_IS_DIGIT
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_ascii_is_digit(
    open_cfw_runtime_vsnprintf_u32 value
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_IS_DIGIT(value) \
    open_cfw_runtime_ascii_is_digit((value))
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_PARSE_DECIMAL
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_parse_decimal(
    const unsigned char **cursor
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_PARSE_DECIMAL(cursor) \
    open_cfw_runtime_parse_decimal((cursor))
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_ntoa_long(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    open_cfw_runtime_vsnprintf_u32 value,
    _Bool negative,
    open_cfw_runtime_vsnprintf_u32 base,
    open_cfw_runtime_vsnprintf_u32 precision,
    open_cfw_runtime_vsnprintf_u32 width,
    open_cfw_runtime_vsnprintf_u32 flags
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG( \
    output, buffer, index, maximum_length, value, negative, base, \
    precision, width, flags \
) \
    open_cfw_runtime_ntoa_long( \
        (output), (buffer), (index), (maximum_length), (value), \
        (negative), (base), (precision), (width), (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG_LONG
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_ntoa_long_long(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    open_cfw_runtime_vsnprintf_u64 value,
    _Bool negative,
    open_cfw_runtime_vsnprintf_u64 base,
    open_cfw_runtime_vsnprintf_u32 precision,
    open_cfw_runtime_vsnprintf_u32 width,
    open_cfw_runtime_vsnprintf_u32 flags
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG_LONG( \
    output, buffer, index, maximum_length, value, negative, base, \
    precision, width, flags \
) \
    open_cfw_runtime_ntoa_long_long( \
        (output), (buffer), (index), (maximum_length), (value), \
        (negative), (base), (precision), (width), (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_FTOA
OPEN_CFW_RUNTIME_FLOAT_ABI
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_ftoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    double value,
    open_cfw_runtime_vsnprintf_u32 precision,
    open_cfw_runtime_vsnprintf_u32 width,
    open_cfw_runtime_vsnprintf_u32 flags
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_FTOA( \
    output, buffer, index, maximum_length, value, precision, width, flags \
) \
    open_cfw_runtime_ftoa( \
        (output), (buffer), (index), (maximum_length), (value), \
        (precision), (width), (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_ETOA
OPEN_CFW_RUNTIME_FLOAT_ABI
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_etoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    double value,
    open_cfw_runtime_vsnprintf_u32 precision,
    open_cfw_runtime_vsnprintf_u32 width,
    open_cfw_runtime_vsnprintf_u32 flags
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_ETOA( \
    output, buffer, index, maximum_length, value, precision, width, flags \
) \
    open_cfw_runtime_etoa( \
        (output), (buffer), (index), (maximum_length), (value), \
        (precision), (width), (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH
open_cfw_runtime_vsnprintf_u32 open_cfw_runtime_vsnprintf_string_length(
    const char *string,
    open_cfw_runtime_vsnprintf_u32 maximum_length
) __asm__("open_cfw_runtime_strnlen_s");
#define OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH(string, maximum_length) \
    open_cfw_runtime_vsnprintf_string_length((string), (maximum_length))
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments) \
    __builtin_va_arg((arguments), open_cfw_runtime_vsnprintf_s32)
#endif
#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U32
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U32(arguments) \
    __builtin_va_arg((arguments), open_cfw_runtime_vsnprintf_u32)
#endif
#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S64
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S64(arguments) \
    __builtin_va_arg((arguments), open_cfw_runtime_vsnprintf_s64)
#endif
#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U64
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U64(arguments) \
    __builtin_va_arg((arguments), open_cfw_runtime_vsnprintf_u64)
#endif
#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE(arguments) \
    __builtin_va_arg((arguments), double)
#endif
#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER
#define OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER(arguments) \
    __builtin_va_arg((arguments), void *)
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT
#define OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT( \
    output, character, buffer, index, maximum_length \
) \
    ((output)( \
        (char)(character), \
        (void *)(buffer), \
        (index), \
        (maximum_length) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION
#define OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION open_cfw_runtime_vsnprintf
#endif

int OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
);

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE
#ifdef OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE_ADDRESS
typedef int (*open_cfw_runtime_vsnprintf_recurse_fn)(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
);
#define OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE( \
    output, buffer, maximum_length, format, arguments \
) \
    ((open_cfw_runtime_vsnprintf_recurse_fn)( \
        (open_cfw_runtime_vsnprintf_uintptr)( \
            OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE_ADDRESS \
        ) | (open_cfw_runtime_vsnprintf_uintptr)1U \
    ))( \
        (output), (buffer), (maximum_length), (format), (arguments) \
    )
#else
#define OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE( \
    output, buffer, maximum_length, format, arguments \
) \
    OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION( \
        (output), (buffer), (maximum_length), (format), (arguments) \
    )
#endif
#endif

static __attribute__((always_inline)) inline
open_cfw_runtime_vsnprintf_u32
open_cfw_runtime_vsnprintf_magnitude_s32(
    open_cfw_runtime_vsnprintf_s32 value
)
{
    open_cfw_runtime_vsnprintf_u32 bits =
        (open_cfw_runtime_vsnprintf_u32)value;

    return value < 0 ? 0U - bits : bits;
}

static __attribute__((always_inline)) inline
open_cfw_runtime_vsnprintf_u64
open_cfw_runtime_vsnprintf_magnitude_s64(
    open_cfw_runtime_vsnprintf_s64 value
)
{
    open_cfw_runtime_vsnprintf_u64 bits =
        (open_cfw_runtime_vsnprintf_u64)value;

    return value < 0 ? 0U - bits : bits;
}

#ifdef OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_HEXFLOAT
static __attribute__((always_inline)) inline char
open_cfw_runtime_vsnprintf_hex_digit(
    open_cfw_runtime_vsnprintf_u32 value,
    open_cfw_runtime_vsnprintf_u32 uppercase
)
{
    return (char)(
        value < 10U
        ? (open_cfw_runtime_vsnprintf_u32)'0' + value
        : (
            (uppercase != 0U
                ? (open_cfw_runtime_vsnprintf_u32)'A'
                : (open_cfw_runtime_vsnprintf_u32)'a')
            + value - 10U
        )
    );
}

static __attribute__((always_inline)) inline
open_cfw_runtime_vsnprintf_u32
open_cfw_runtime_vsnprintf_hexfloat(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    open_cfw_runtime_vsnprintf_u32 index,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    double value,
    open_cfw_runtime_vsnprintf_u32 precision,
    open_cfw_runtime_vsnprintf_u32 width,
    open_cfw_runtime_vsnprintf_u32 flags
)
{
    union {
        double floating;
        open_cfw_runtime_vsnprintf_u64 bits;
    } representation;
    open_cfw_runtime_vsnprintf_u64 fraction;
    open_cfw_runtime_vsnprintf_u32 raw_exponent;
    open_cfw_runtime_vsnprintf_u32 uppercase =
        flags & OPEN_CFW_RUNTIME_VSNPRINTF_UPPER;
    open_cfw_runtime_vsnprintf_u32 negative;
    open_cfw_runtime_vsnprintf_u32 explicit_precision =
        flags & OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION;
    open_cfw_runtime_vsnprintf_u32 sign_length;
    open_cfw_runtime_vsnprintf_u32 length;
    open_cfw_runtime_vsnprintf_u32 exponent_digits;
    open_cfw_runtime_vsnprintf_u32 iterator;
    open_cfw_runtime_vsnprintf_u32 leading;
    open_cfw_runtime_vsnprintf_u32 padding;
    int exponent;
    int exponent_magnitude;
    char sign = 0;

#define OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(character) \
    do { \
        OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT( \
            output, character, buffer, index, maximum_length \
        ); \
        index += 1U; \
    } while (0)

    representation.floating = value;
    negative = (open_cfw_runtime_vsnprintf_u32)(
        representation.bits >> 63U
    );
    raw_exponent = (open_cfw_runtime_vsnprintf_u32)(
        representation.bits >> 52U
    ) & 0x7FFU;
    fraction = representation.bits & 0x000FFFFFFFFFFFFFULL;
    if (negative != 0U) {
        sign = '-';
    }
    else if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_PLUS) != 0U) {
        sign = '+';
    }
    else if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_SPACE) != 0U) {
        sign = ' ';
    }
    sign_length = sign != 0 ? 1U : 0U;

    if (raw_exponent == 0x7FFU) {
        length = sign_length + 3U;
        padding = width > length ? width - length : 0U;
        if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) == 0U) {
            while (padding-- != 0U) {
                OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(' ');
            }
        }
        if (sign != 0) {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(sign);
        }
        if (fraction == 0U) {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'I' : 'i'
            );
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'N' : 'n'
            );
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'F' : 'f'
            );
        }
        else {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'N' : 'n'
            );
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'A' : 'a'
            );
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                uppercase != 0U ? 'N' : 'n'
            );
        }
        if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) != 0U) {
            while (padding-- != 0U) {
                OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(' ');
            }
        }
        return index;
    }

    if (raw_exponent == 0U) {
        if (fraction == 0U) {
            leading = 0U;
            exponent = 0;
        }
        else {
            open_cfw_runtime_vsnprintf_u32 highest = 51U;

            while ((fraction & ((open_cfw_runtime_vsnprintf_u64)1U << highest)) == 0U) {
                highest -= 1U;
            }
            exponent = (int)highest - 1074;
            fraction = (
                fraction ^ ((open_cfw_runtime_vsnprintf_u64)1U << highest)
            ) << (52U - highest);
            leading = 1U;
        }
    }
    else {
        leading = 1U;
        exponent = (int)raw_exponent - 1023;
    }

    if (explicit_precision == 0U) {
        precision = 13U;
        while (precision != 0U && (fraction & 0xFU) == 0U) {
            fraction >>= 4U;
            precision -= 1U;
        }
        fraction <<= (13U - precision) * 4U;
    }
    else if (precision < 13U) {
        open_cfw_runtime_vsnprintf_u32 shift = 52U - precision * 4U;
        open_cfw_runtime_vsnprintf_u64 kept = fraction >> shift;
        open_cfw_runtime_vsnprintf_u64 discarded = fraction & (
            ((open_cfw_runtime_vsnprintf_u64)1U << shift) - 1U
        );
        open_cfw_runtime_vsnprintf_u64 halfway =
            (open_cfw_runtime_vsnprintf_u64)1U << (shift - 1U);

        if (discarded > halfway || (discarded == halfway && (kept & 1U) != 0U)) {
            kept += 1U;
            if (kept == ((open_cfw_runtime_vsnprintf_u64)1U << (precision * 4U))) {
                leading += 1U;
                kept = 0U;
            }
        }
        fraction = kept << shift;
    }

    exponent_magnitude = exponent < 0 ? -exponent : exponent;
    exponent_digits = 1U;
    for (iterator = (open_cfw_runtime_vsnprintf_u32)exponent_magnitude;
         iterator >= 10U; iterator /= 10U) {
        exponent_digits += 1U;
    }
    length = sign_length + 2U + 1U + 2U + exponent_digits + precision;
    if (precision != 0U || (flags & OPEN_CFW_RUNTIME_VSNPRINTF_HASH) != 0U) {
        length += 1U;
    }
    padding = width > length ? width - length : 0U;
    if ((flags & (OPEN_CFW_RUNTIME_VSNPRINTF_LEFT | OPEN_CFW_RUNTIME_VSNPRINTF_ZERO_PAD)) == 0U) {
        while (padding-- != 0U) {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(' ');
        }
    }
    if (sign != 0) {
        OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(sign);
    }
    OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT('0');
    OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(uppercase != 0U ? 'X' : 'x');
    if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) == 0U
        && (flags & OPEN_CFW_RUNTIME_VSNPRINTF_ZERO_PAD) != 0U) {
        while (padding-- != 0U) {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT('0');
        }
    }
    OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
        open_cfw_runtime_vsnprintf_hex_digit(leading, uppercase)
    );
    if (precision != 0U || (flags & OPEN_CFW_RUNTIME_VSNPRINTF_HASH) != 0U) {
        OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT('.');
    }
    for (iterator = 0U; iterator < precision; iterator += 1U) {
        open_cfw_runtime_vsnprintf_u32 digit = 0U;

        if (iterator < 13U) {
            digit = (open_cfw_runtime_vsnprintf_u32)(
                fraction >> (48U - iterator * 4U)
            ) & 0xFU;
        }
        OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
            open_cfw_runtime_vsnprintf_hex_digit(digit, uppercase)
        );
    }
    OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(uppercase != 0U ? 'P' : 'p');
    OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(exponent < 0 ? '-' : '+');
    {
        open_cfw_runtime_vsnprintf_u32 divisor = 1U;

        for (iterator = 1U; iterator < exponent_digits; iterator += 1U) {
            divisor *= 10U;
        }
        do {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(
                '0' + (exponent_magnitude / (int)divisor) % 10
            );
            divisor /= 10U;
        } while (divisor != 0U);
    }
    if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) != 0U) {
        while (padding-- != 0U) {
            OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT(' ');
        }
    }
    return index;

#undef OPEN_CFW_RUNTIME_VSNPRINTF_HEXFLOAT_OUTPUT
}
#endif

__attribute__((used, noinline))
int OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
)
{
    open_cfw_runtime_vsnprintf_u32 index = 0U;

    if (buffer == (unsigned char *)0) {
        output = OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT;
    }

    while (*format != 0U) {
        open_cfw_runtime_vsnprintf_u32 flags;
        open_cfw_runtime_vsnprintf_u32 width;
        open_cfw_runtime_vsnprintf_u32 precision;
        open_cfw_runtime_vsnprintf_u32 keep_parsing;
        unsigned int specifier;

        if (*format != (unsigned char)'%') {
            OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                output,
                *format,
                buffer,
                index,
                maximum_length
            );
            index += 1U;
            format += 1;
            continue;
        }
        format += 1;

        flags = 0U;
        do {
            keep_parsing = 1U;
            switch (*format) {
            case '0':
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_ZERO_PAD;
                format += 1;
                break;
            case '-':
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LEFT;
                format += 1;
                break;
            case '+':
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_PLUS;
                format += 1;
                break;
            case ' ':
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_SPACE;
                format += 1;
                break;
            case '#':
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_HASH;
                format += 1;
                break;
            default:
                keep_parsing = 0U;
                break;
            }
        } while (keep_parsing != 0U);

        width = 0U;
        if (OPEN_CFW_RUNTIME_VSNPRINTF_IS_DIGIT(*format) != 0U) {
            width = OPEN_CFW_RUNTIME_VSNPRINTF_PARSE_DECIMAL(&format);
        }
        else if (*format == (unsigned char)'*') {
            open_cfw_runtime_vsnprintf_s32 requested_width =
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);

            if (requested_width < 0) {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LEFT;
                width = open_cfw_runtime_vsnprintf_magnitude_s32(
                    requested_width
                );
            }
            else {
                width = (open_cfw_runtime_vsnprintf_u32)requested_width;
            }
            format += 1;
        }

        precision = 0U;
        if (*format == (unsigned char)'.') {
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION;
            format += 1;
            if (OPEN_CFW_RUNTIME_VSNPRINTF_IS_DIGIT(*format) != 0U) {
                precision =
                    OPEN_CFW_RUNTIME_VSNPRINTF_PARSE_DECIMAL(&format);
            }
            else if (*format == (unsigned char)'*') {
                open_cfw_runtime_vsnprintf_s32 requested_precision =
                    OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);

                precision = (
                    requested_precision > 0
                    ? (open_cfw_runtime_vsnprintf_u32)requested_precision
                    : 0U
                );
                format += 1;
            }
        }

        switch (*format) {
        case 'l':
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LONG;
            format += 1;
            if (*format == (unsigned char)'l') {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG;
                format += 1;
            }
            break;
        case 'h':
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_SHORT;
            format += 1;
            if (*format == (unsigned char)'h') {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_CHAR;
                format += 1;
            }
            break;
        case 't':
        case 'z':
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LONG;
            format += 1;
            break;
        case 'j':
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG;
            format += 1;
            break;
#ifdef OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_IAR_LENGTHS
        case 'q':
            flags |= OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG;
            format += 1;
            break;
        case 'L':
            /* IAR's G2 ABI stores long double in the same 64-bit slot. */
            format += 1;
            break;
#endif
        default:
            break;
        }

        specifier = *format;
        switch (specifier) {
        case 'd':
        case 'i':
        case 'u':
        case 'x':
        case 'X':
        case 'o':
        case 'b':
        case 'p':
        case 'P': {
            open_cfw_runtime_vsnprintf_u32 base;
            _Bool pointer_specifier = (
                specifier == (unsigned int)'p'
                || specifier == (unsigned int)'P'
            );
            _Bool uppercase_pointer =
                specifier == (unsigned int)'P';

            if (
                specifier == (unsigned int)'x'
                || specifier == (unsigned int)'X'
                || pointer_specifier != 0
            ) {
                base = 16U;
            }
            else if (specifier == (unsigned int)'o') {
                base = 8U;
            }
            else if (specifier == (unsigned int)'b') {
                base = 2U;
            }
            else {
                base = 10U;
                flags &= ~OPEN_CFW_RUNTIME_VSNPRINTF_HASH;
            }

            if (pointer_specifier != 0) {
                flags |= (
                    OPEN_CFW_RUNTIME_VSNPRINTF_HASH
                    | OPEN_CFW_RUNTIME_VSNPRINTF_LONG
                );
                if (format[1] == (unsigned char)'V') {
                    format += 1;
                    specifier = *format;
                }
            }
            if (
                specifier == (unsigned int)'X'
                || uppercase_pointer != 0
            ) {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_UPPER;
            }
            if (
                specifier != (unsigned int)'i'
                && specifier != (unsigned int)'d'
            ) {
                flags &= ~(
                    OPEN_CFW_RUNTIME_VSNPRINTF_PLUS
                    | OPEN_CFW_RUNTIME_VSNPRINTF_SPACE
                );
            }
            if (
                (flags & OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION) != 0U
            ) {
                flags &= ~OPEN_CFW_RUNTIME_VSNPRINTF_ZERO_PAD;
            }

            if (
                specifier == (unsigned int)'i'
                || specifier == (unsigned int)'d'
            ) {
                if (
                    (flags & OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG) != 0U
                ) {
                    open_cfw_runtime_vsnprintf_s64 value =
                        OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S64(arguments);

                    index = OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG_LONG(
                        output,
                        buffer,
                        index,
                        maximum_length,
                        open_cfw_runtime_vsnprintf_magnitude_s64(value),
                        value < 0,
                        base,
                        precision,
                        width,
                        flags
                    );
                }
                else {
                    open_cfw_runtime_vsnprintf_s32 value;

                    if (
                        (flags & OPEN_CFW_RUNTIME_VSNPRINTF_LONG) != 0U
                    ) {
                        value =
                            OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);
                    }
                    else if (
                        (flags & OPEN_CFW_RUNTIME_VSNPRINTF_CHAR) != 0U
                    ) {
                        /*
                         * Firmware plain char is unsigned: stock uses UXTB
                         * here even for the signed d/i conversion path.
                         */
                        value = (unsigned char)
                            OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);
                    }
                    else if (
                        (flags & OPEN_CFW_RUNTIME_VSNPRINTF_SHORT) != 0U
                    ) {
                        value = (short)
                            OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);
                    }
                    else {
                        value =
                            OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments);
                    }
                    index = OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG(
                        output,
                        buffer,
                        index,
                        maximum_length,
                        open_cfw_runtime_vsnprintf_magnitude_s32(value),
                        value < 0,
                        base,
                        precision,
                        width,
                        flags
                    );
                }
            }
            else if (specifier == (unsigned int)'V') {
                struct open_cfw_runtime_vsnprintf_recursive *recursive =
                    (struct open_cfw_runtime_vsnprintf_recursive *)
                    OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER(arguments);
                unsigned char *nested_buffer = (
                    (unsigned char *)(
                        (open_cfw_runtime_vsnprintf_uintptr)buffer
                        + (open_cfw_runtime_vsnprintf_uintptr)index
                    )
                );

                index += (open_cfw_runtime_vsnprintf_u32)
                    OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE(
                        output,
                        nested_buffer,
                        maximum_length - index,
                        recursive->format,
                        *recursive->arguments
                    );
            }
            else if (
                (flags & OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG) != 0U
            ) {
                index = OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG_LONG(
                    output,
                    buffer,
                    index,
                    maximum_length,
                    OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U64(arguments),
                    0,
                    base,
                    precision,
                    width,
                    flags
                );
            }
            else {
                open_cfw_runtime_vsnprintf_u32 value;

                if (pointer_specifier != 0) {
                    value = (open_cfw_runtime_vsnprintf_u32)
                        (open_cfw_runtime_vsnprintf_uintptr)
                        OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER(arguments);
                }
                else {
                    value =
                        OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U32(arguments);
                    if (
                        (flags & OPEN_CFW_RUNTIME_VSNPRINTF_CHAR) != 0U
                    ) {
                        value = (unsigned char)value;
                    }
                    else if (
                        (flags & OPEN_CFW_RUNTIME_VSNPRINTF_SHORT) != 0U
                    ) {
                        value = (unsigned short)value;
                    }
                }
                index = OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG(
                    output,
                    buffer,
                    index,
                    maximum_length,
                    value,
                    0,
                    base,
                    precision,
                    width,
                    flags
                );
            }
            format += 1;
            break;
        }

        case 'f':
        case 'F':
            if (specifier == (unsigned int)'F') {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_UPPER;
            }
            index = OPEN_CFW_RUNTIME_VSNPRINTF_FTOA(
                output,
                buffer,
                index,
                maximum_length,
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE(arguments),
                precision,
                width,
                flags
            );
            format += 1;
            break;

        case 'e':
        case 'E':
        case 'g':
        case 'G':
            if (
                specifier == (unsigned int)'g'
                || specifier == (unsigned int)'G'
            ) {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_ADAPT_EXP;
            }
            if (
                specifier == (unsigned int)'E'
                || specifier == (unsigned int)'G'
            ) {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_UPPER;
            }
            index = OPEN_CFW_RUNTIME_VSNPRINTF_ETOA(
                output,
                buffer,
                index,
                maximum_length,
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE(arguments),
                precision,
                width,
                flags
            );
            format += 1;
            break;

#ifdef OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_HEXFLOAT
        case 'a':
        case 'A':
            if (specifier == (unsigned int)'A') {
                flags |= OPEN_CFW_RUNTIME_VSNPRINTF_UPPER;
            }
            index = open_cfw_runtime_vsnprintf_hexfloat(
                output,
                buffer,
                index,
                maximum_length,
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE(arguments),
                precision,
                width,
                flags
            );
            format += 1;
            break;
#endif

        case 'c': {
            open_cfw_runtime_vsnprintf_u32 length = 1U;

            if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) == 0U) {
                while (length++ < width) {
                    OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                        output,
                        ' ',
                        buffer,
                        index,
                        maximum_length
                    );
                    index += 1U;
                }
            }
            OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                output,
                (unsigned char)
                    OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32(arguments),
                buffer,
                index,
                maximum_length
            );
            index += 1U;
            if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) != 0U) {
                while (length++ < width) {
                    OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                        output,
                        ' ',
                        buffer,
                        index,
                        maximum_length
                    );
                    index += 1U;
                }
            }
            format += 1;
            break;
        }

        case 's': {
            const char *string = (const char *)
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER(arguments);
            open_cfw_runtime_vsnprintf_u32 length =
                OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH(
                    string,
                    precision != 0U ? precision : 0xFFFFFFFFU
                );
            open_cfw_runtime_vsnprintf_u32 padded_length;

            if (
                (flags & OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION) != 0U
                && length >= precision
            ) {
                length = precision;
            }
            padded_length = length;
            if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) == 0U) {
                while (padded_length++ < width) {
                    OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                        output,
                        ' ',
                        buffer,
                        index,
                        maximum_length
                    );
                    index += 1U;
                }
            }
            while (
                *string != '\0'
                && (
                    (flags & OPEN_CFW_RUNTIME_VSNPRINTF_PRECISION) == 0U
                    || precision-- != 0U
                )
            ) {
                OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                    output,
                    *string,
                    buffer,
                    index,
                    maximum_length
                );
                string += 1;
                index += 1U;
            }
            if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LEFT) != 0U) {
                while (padded_length++ < width) {
                    OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                        output,
                        ' ',
                        buffer,
                        index,
                        maximum_length
                    );
                    index += 1U;
                }
            }
            format += 1;
            break;
        }

#ifdef OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_COUNT
        case 'n': {
            void *destination =
                OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER(arguments);

            if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LONG_LONG) != 0U) {
                *(open_cfw_runtime_vsnprintf_s64 *)destination =
                    (open_cfw_runtime_vsnprintf_s64)index;
            }
            else if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_LONG) != 0U) {
                *(long *)destination = (long)index;
            }
            else if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_CHAR) != 0U) {
                *(signed char *)destination = (signed char)index;
            }
            else if ((flags & OPEN_CFW_RUNTIME_VSNPRINTF_SHORT) != 0U) {
                *(short *)destination = (short)index;
            }
            else {
                *(int *)destination = (int)index;
            }
            format += 1;
            break;
        }
#endif

        case '%':
            OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                output,
                '%',
                buffer,
                index,
                maximum_length
            );
            index += 1U;
            format += 1;
            break;

        default:
            OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
                output,
                *format,
                buffer,
                index,
                maximum_length
            );
            index += 1U;
            format += 1;
            break;
        }
    }

    OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT(
        output,
        0,
        buffer,
        index < maximum_length ? index : maximum_length - 1U,
        maximum_length
    );
    return (int)index;
}

#undef OPEN_CFW_RUNTIME_VSNPRINTF_CALL_OUTPUT
#undef OPEN_CFW_RUNTIME_VSNPRINTF_ETOA
#undef OPEN_CFW_RUNTIME_VSNPRINTF_FTOA
#undef OPEN_CFW_RUNTIME_VSNPRINTF_IS_DIGIT
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_DOUBLE
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_POINTER
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S32
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_S64
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U32
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NEXT_U64
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NOOP_OUTPUT
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG
#undef OPEN_CFW_RUNTIME_VSNPRINTF_NTOA_LONG_LONG
#undef OPEN_CFW_RUNTIME_VSNPRINTF_PARSE_DECIMAL
#undef OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE
#undef OPEN_CFW_RUNTIME_VSNPRINTF_STRING_LENGTH
#undef OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION
