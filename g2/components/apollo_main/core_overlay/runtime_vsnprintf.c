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

int open_cfw_runtime_vsnprintf(
    open_cfw_runtime_ntoa_output_fn output,
    unsigned char *buffer,
    open_cfw_runtime_vsnprintf_u32 maximum_length,
    const unsigned char *format,
    __builtin_va_list arguments
);

#ifndef OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE
#define OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE( \
    output, buffer, maximum_length, format, arguments \
) \
    open_cfw_runtime_vsnprintf( \
        (output), (buffer), (maximum_length), (format), (arguments) \
    )
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

__attribute__((used, noinline))
int open_cfw_runtime_vsnprintf(
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
