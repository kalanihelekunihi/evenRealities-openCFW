/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 application logging formatter core
 * at 0x00473036. The bounded floating converter at 0x00472EF6 remains a
 * reviewed compatibility ABI.
 */

typedef unsigned char open_cfw_log_core_u8;
typedef unsigned int open_cfw_log_core_u32;
typedef __UINTPTR_TYPE__ open_cfw_log_core_uintptr;

typedef struct {
    unsigned int low;
    unsigned int high;
} open_cfw_log_core_u64_words;

unsigned int open_cfw_log_decimal_digits(
    unsigned int low,
    unsigned int high
);
unsigned int open_cfw_log_signed_decimal_digits(
    unsigned int low,
    unsigned int high
);
unsigned int open_cfw_log_hex_digits(
    unsigned int low,
    unsigned int high
);
int open_cfw_log_parse_integer(
    const unsigned char *text,
    unsigned int *consumed
);
unsigned int open_cfw_log_decimal_write(
    unsigned int low,
    unsigned int high,
    char *destination
);
unsigned int open_cfw_log_hex_write(
    unsigned int low,
    unsigned int high,
    char *destination,
    unsigned int lowercase
);
unsigned int open_cfw_log_string_length(const char *text);
unsigned int open_cfw_log_padding_write(
    char *destination,
    unsigned int fill,
    int count
);

#ifndef OPEN_CFW_LOG_CORE_CRLF_ENABLED
#define OPEN_CFW_LOG_CORE_CRLF_ENABLED() \
    (*(volatile open_cfw_log_core_u8 *)(void *)0x20074F7FU)
#endif

#ifndef OPEN_CFW_LOG_CORE_FLOAT_WRITE
typedef int __attribute__((pcs("aapcs-vfp")))
    open_cfw_log_core_float_write_signature(
        char *destination,
        unsigned int precision,
        float value
    );
#define OPEN_CFW_LOG_CORE_FLOAT_WRITE(destination, precision, value) \
    (((open_cfw_log_core_float_write_signature *)0x00472EF7U)( \
        (destination), \
        (precision), \
        (value) \
    ))
#endif

#ifndef OPEN_CFW_LOG_CORE_CONVERT_DOUBLE
static __attribute__((always_inline)) inline float
open_cfw_log_core_convert_double_default(double value)
{
    float result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vcvt.f32.f64 %0, %P1"
        : "=t"(result)
        : "w"(value)
    );
    return result;
}
#define OPEN_CFW_LOG_CORE_CONVERT_DOUBLE(value) \
    open_cfw_log_core_convert_double_default(value)
#endif

static __attribute__((always_inline)) inline unsigned int
open_cfw_log_core_read_u32_default(open_cfw_log_core_u8 **cursor)
{
    unsigned int value = *(const unsigned int *)(const void *)*cursor;

    *cursor += 4;
    return value;
}

static __attribute__((always_inline)) inline const char *
open_cfw_log_core_read_pointer_default(open_cfw_log_core_u8 **cursor)
{
    return (const char *)(open_cfw_log_core_uintptr)
        open_cfw_log_core_read_u32_default(cursor);
}

static __attribute__((always_inline)) inline open_cfw_log_core_u64_words
open_cfw_log_core_read_u64_default(open_cfw_log_core_u8 **cursor)
{
    open_cfw_log_core_uintptr aligned =
        ((open_cfw_log_core_uintptr)*cursor + 7U)
        & ~(open_cfw_log_core_uintptr)7U;
    const unsigned int *words =
        (const unsigned int *)(const void *)aligned;
    open_cfw_log_core_u64_words value;

    value.low = words[0];
    value.high = words[1];
    *cursor = (open_cfw_log_core_u8 *)(aligned + 8U);
    return value;
}

static __attribute__((always_inline)) inline double
open_cfw_log_core_read_double_default(open_cfw_log_core_u8 **cursor)
{
    open_cfw_log_core_uintptr aligned =
        ((open_cfw_log_core_uintptr)*cursor + 7U)
        & ~(open_cfw_log_core_uintptr)7U;
    double value = *(const double *)(const void *)aligned;

    *cursor = (open_cfw_log_core_u8 *)(aligned + 8U);
    return value;
}

#ifndef OPEN_CFW_LOG_CORE_READ_U32
#define OPEN_CFW_LOG_CORE_READ_U32(cursor) \
    open_cfw_log_core_read_u32_default(&(cursor))
#endif

#ifndef OPEN_CFW_LOG_CORE_READ_POINTER
#define OPEN_CFW_LOG_CORE_READ_POINTER(cursor) \
    open_cfw_log_core_read_pointer_default(&(cursor))
#endif

#ifndef OPEN_CFW_LOG_CORE_READ_U64
#define OPEN_CFW_LOG_CORE_READ_U64(cursor) \
    open_cfw_log_core_read_u64_default(&(cursor))
#endif

#ifndef OPEN_CFW_LOG_CORE_READ_DOUBLE
#define OPEN_CFW_LOG_CORE_READ_DOUBLE(cursor) \
    open_cfw_log_core_read_double_default(&(cursor))
#endif

static __attribute__((always_inline)) inline void
open_cfw_log_core_put(
    char **destination,
    unsigned int *total,
    char value
)
{
    if (*destination != (char *)0) {
        **destination = value;
        *destination += 1;
    }
    *total += 1U;
}

static __attribute__((always_inline)) inline void
open_cfw_log_core_pad(
    char **destination,
    unsigned int *total,
    unsigned int fill,
    unsigned int count
)
{
    unsigned int written = open_cfw_log_padding_write(
        *destination,
        fill,
        (int)count
    );

    if (*destination != (char *)0) {
        *destination += written;
    }
    *total += written;
}

static __attribute__((always_inline)) inline void
open_cfw_log_core_advance_after_write(
    char **destination,
    unsigned int *total,
    unsigned int written
)
{
    if (*destination != (char *)0) {
        *destination += written;
    }
    *total += written;
}

__attribute__((used, noinline))
unsigned int open_cfw_log_format_core(
    char *destination,
    const char *format,
    void *argument_cursor
)
{
    open_cfw_log_core_u8 *arguments =
        (open_cfw_log_core_u8 *)argument_cursor;
    unsigned int total = 0U;

    while (*format != '\0') {
        unsigned int width;
        unsigned int precision = 0xFFFFFFFFU;
        unsigned int consumed;
        unsigned int long_long = 0U;
        unsigned int fill = (unsigned int)' ';
        unsigned int lowercase = 0U;
        char conversion;

        if (*format != '%') {
            if (
                destination != (char *)0
                && *format == '\n'
                && OPEN_CFW_LOG_CORE_CRLF_ENABLED() != 0U
            ) {
                open_cfw_log_core_put(&destination, &total, '\r');
            }
            open_cfw_log_core_put(&destination, &total, *format);
            format += 1;
            continue;
        }

        format += 1;
        if (*format == '0') {
            fill = (unsigned int)'0';
            format += 1;
        }
        width = (unsigned int)open_cfw_log_parse_integer(
            (const unsigned char *)format,
            &consumed
        );
        format += consumed;
        if ((*format != 's') && ((int)width < 0)) {
            width = 0U - width;
        }
        if (*format == '.') {
            format += 1;
            if (*format == '*') {
                precision = OPEN_CFW_LOG_CORE_READ_U32(arguments);
                format += 1;
            } else {
                precision = (unsigned int)open_cfw_log_parse_integer(
                    (const unsigned char *)format,
                    &consumed
                );
                format += consumed;
            }
        }
        if (*format == 'l') {
            format += 1;
            if (*format == 'l') {
                long_long = 1U;
                format += 1;
            }
        }
        conversion = *format;

        if ((conversion == 'f') || (conversion == 'F')) {
            if (destination != (char *)0) {
                double source = OPEN_CFW_LOG_CORE_READ_DOUBLE(arguments);
                int written;

                destination[0] = (char)20;
                destination[1] = '\0';
                destination[2] = '\0';
                destination[3] = '\0';
                written = OPEN_CFW_LOG_CORE_FLOAT_WRITE(
                    destination,
                    precision,
                    OPEN_CFW_LOG_CORE_CONVERT_DOUBLE(source)
                );
                if (written < 0) {
                    unsigned int fallback = written == -1
                        ? 0x00302E30U
                        : (
                            written == -2
                                ? 0x00232E23U
                                : 0x003F2E3FU
                        );

                    destination[0] = (char)fallback;
                    destination[1] = (char)(fallback >> 8U);
                    destination[2] = (char)(fallback >> 16U);
                    destination[3] = (char)(fallback >> 24U);
                    written = 3;
                }
                destination += (unsigned int)written;
                total += (unsigned int)written;
            }
        } else if ((conversion == 'x') || (conversion == 'X')) {
            open_cfw_log_core_u64_words value;
            unsigned int written;

            if (conversion == 'x') {
                lowercase = 1U;
            }
            if (long_long != 0U) {
                value = OPEN_CFW_LOG_CORE_READ_U64(arguments);
            } else {
                value.low = OPEN_CFW_LOG_CORE_READ_U32(arguments);
                value.high = 0U;
            }
            if (width != 0U) {
                unsigned int digits = open_cfw_log_hex_digits(
                    value.low,
                    value.high
                );

                open_cfw_log_core_pad(
                    &destination,
                    &total,
                    fill,
                    width - digits
                );
            }
            written = open_cfw_log_hex_write(
                value.low,
                value.high,
                destination,
                lowercase
            );
            open_cfw_log_core_advance_after_write(
                &destination,
                &total,
                written
            );
        } else if (conversion == 'c') {
            open_cfw_log_core_put(
                &destination,
                &total,
                (char)OPEN_CFW_LOG_CORE_READ_U32(arguments)
            );
        } else if ((conversion == 'd') || (conversion == 'i')) {
            open_cfw_log_core_u64_words value;
            unsigned int negative;
            unsigned int written;

            if (long_long != 0U) {
                value = OPEN_CFW_LOG_CORE_READ_U64(arguments);
            } else {
                value.low = OPEN_CFW_LOG_CORE_READ_U32(arguments);
                value.high = (value.low & 0x80000000U) != 0U
                    ? 0xFFFFFFFFU
                    : 0U;
            }
            negative = (value.high & 0x80000000U) != 0U ? 1U : 0U;
            if (negative != 0U) {
                unsigned int borrow = value.low != 0U ? 1U : 0U;

                value.low = 0U - value.low;
                value.high = (0U - value.high) - borrow;
            }
            if (width == 0U) {
                if (negative != 0U) {
                    open_cfw_log_core_put(&destination, &total, '-');
                }
            } else {
                unsigned int digits = open_cfw_log_signed_decimal_digits(
                    value.low,
                    value.high
                );
                unsigned int padding = width - digits;

                if (negative != 0U) {
                    padding -= 1U;
                    if (fill == (unsigned int)'0') {
                        open_cfw_log_core_put(
                            &destination,
                            &total,
                            '-'
                        );
                    }
                }
                open_cfw_log_core_pad(
                    &destination,
                    &total,
                    fill,
                    padding
                );
                if (
                    negative != 0U
                    && fill == (unsigned int)' '
                ) {
                    open_cfw_log_core_put(&destination, &total, '-');
                }
            }
            written = open_cfw_log_decimal_write(
                value.low,
                value.high,
                destination
            );
            open_cfw_log_core_advance_after_write(
                &destination,
                &total,
                written
            );
        } else if (conversion == 's') {
            const char *text = OPEN_CFW_LOG_CORE_READ_POINTER(arguments);
            unsigned int remaining = open_cfw_log_string_length(text);

            if (((int)precision >= 0) && (precision < remaining)) {
                remaining = precision;
            }
            if (((int)width > 0) && (remaining < width)) {
                open_cfw_log_core_pad(
                    &destination,
                    &total,
                    fill,
                    width - remaining
                );
                width = 0U;
            }
            while ((*text != '\0') && (remaining != 0U)) {
                open_cfw_log_core_put(
                    &destination,
                    &total,
                    *text
                );
                text += 1;
                remaining -= 1U;
            }
            if (width != 0U) {
                unsigned int trailing = 0U - width;

                if (remaining < trailing) {
                    open_cfw_log_core_pad(
                        &destination,
                        &total,
                        fill,
                        trailing - remaining
                    );
                }
            }
        } else if (conversion == 'u') {
            open_cfw_log_core_u64_words value;
            unsigned int written;

            if (long_long != 0U) {
                value = OPEN_CFW_LOG_CORE_READ_U64(arguments);
            } else {
                value.low = OPEN_CFW_LOG_CORE_READ_U32(arguments);
                value.high = 0U;
            }
            if (width != 0U) {
                unsigned int digits = open_cfw_log_decimal_digits(
                    value.low,
                    value.high
                );

                open_cfw_log_core_pad(
                    &destination,
                    &total,
                    fill,
                    width - digits
                );
            }
            written = open_cfw_log_decimal_write(
                value.low,
                value.high,
                destination
            );
            open_cfw_log_core_advance_after_write(
                &destination,
                &total,
                written
            );
        } else {
            open_cfw_log_core_put(
                &destination,
                &total,
                conversion
            );
        }
        format += 1;
    }
    if (destination != (char *)0) {
        *destination = '\0';
    }
    return total;
}
