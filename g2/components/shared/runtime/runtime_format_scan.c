/*
 * SPDX-License-Identifier: MIT
 *
 * Freestanding formatted-input and floating parser used to replace the
 * retained IAR DLIB scanf/strtod cluster in the G2 firmware.  It deliberately
 * uses no locale, heap, errno, or host C-library service.  The accepted input
 * grammar covers the conversions used by ISO C sscanf: integer, decimal and
 * hexadecimal floating point, strings, characters, scansets, pointers, %n,
 * field widths, assignment suppression, and hh/h/l/ll/j/z/t/L modifiers.
 */

#include "runtime_format_scan.h"

#include <stddef.h>
#include <stdint.h>

enum open_cfw_scan_length {
    OPEN_CFW_SCAN_DEFAULT,
    OPEN_CFW_SCAN_HH,
    OPEN_CFW_SCAN_H,
    OPEN_CFW_SCAN_L,
    OPEN_CFW_SCAN_LL,
    OPEN_CFW_SCAN_J,
    OPEN_CFW_SCAN_Z,
    OPEN_CFW_SCAN_T,
    OPEN_CFW_SCAN_CAP_L
};

static int open_cfw_scan_space(unsigned int value)
{
    return value == ' ' || (value >= '\t' && value <= '\r');
}

static int open_cfw_scan_digit(unsigned int value)
{
    return value >= '0' && value <= '9';
}

static int open_cfw_scan_hex_value(unsigned int value)
{
    if (value >= '0' && value <= '9') {
        return (int)(value - '0');
    }
    value |= 0x20U;
    if (value >= 'a' && value <= 'f') {
        return (int)(value - 'a' + 10U);
    }
    return -1;
}

static unsigned int open_cfw_scan_lower(unsigned int value)
{
    return value >= 'A' && value <= 'Z' ? value + 0x20U : value;
}

static int open_cfw_scan_within(
    const char *start,
    const char *cursor,
    unsigned int maximum,
    unsigned int needed
)
{
    size_t used;

    if (maximum == ~0U) {
        return 1;
    }
    used = (size_t)(cursor - start);
    return used <= (size_t)maximum
        && (size_t)needed <= (size_t)maximum - used;
}

static int open_cfw_scan_word_equal(
    const char *start,
    const char *cursor,
    unsigned int maximum,
    const char *word
)
{
    while (*word != '\0') {
        if (!open_cfw_scan_within(start, cursor, maximum, 1U)
            || *cursor == '\0') {
            return 0;
        }
        if (open_cfw_scan_lower((unsigned char)*cursor)
            != (unsigned char)*word) {
            return 0;
        }
        ++cursor;
        ++word;
    }
    return 1;
}

static __attribute__((always_inline)) inline double open_cfw_scan_scale(
    double value,
    unsigned int base,
    int exponent
)
{
    double factor = (double)base;
    unsigned int magnitude = exponent < 0
        ? (unsigned int)(-(exponent + 1)) + 1U
        : (unsigned int)exponent;

    while (magnitude != 0U) {
        if ((magnitude & 1U) != 0U) {
            value = exponent < 0 ? value / factor : value * factor;
        }
        magnitude >>= 1U;
        if (magnitude != 0U) {
            factor *= factor;
        }
    }
    return value;
}

double open_cfw_runtime_strtod_bounded(
    const char *input,
    unsigned int maximum,
    const char **end
)
{
    const char *cursor = input;
    const char *number_start;
    double value = 0.0;
    int negative = 0;
    int digits = 0;
    int exponent = 0;

    while (open_cfw_scan_within(input, cursor, maximum, 1U)
           && open_cfw_scan_space((unsigned char)*cursor)) {
        ++cursor;
    }
    number_start = cursor;
    if (open_cfw_scan_within(input, cursor, maximum, 1U)
        && (*cursor == '+' || *cursor == '-')) {
        negative = *cursor == '-';
        ++cursor;
    }
    if (open_cfw_scan_word_equal(input, cursor, maximum, "infinity")) {
        cursor += 8;
        value = __builtin_inf();
        goto done;
    }
    if (open_cfw_scan_word_equal(input, cursor, maximum, "inf")) {
        cursor += 3;
        value = __builtin_inf();
        goto done;
    }
    if (open_cfw_scan_word_equal(input, cursor, maximum, "nan")) {
        cursor += 3;
        if (open_cfw_scan_within(input, cursor, maximum, 1U)
            && *cursor == '(') {
            const char *payload = cursor + 1;
            while (open_cfw_scan_within(input, payload, maximum, 1U)
                   && (open_cfw_scan_digit((unsigned char)*payload)
                   || ((open_cfw_scan_lower((unsigned char)*payload) >= 'a')
                       && (open_cfw_scan_lower((unsigned char)*payload) <= 'z'))
                   || *payload == '_')) {
                ++payload;
            }
            if (open_cfw_scan_within(input, payload, maximum, 1U)
                && *payload == ')') {
                cursor = payload + 1;
            }
        }
        value = __builtin_nan("");
        goto done;
    }

    if (open_cfw_scan_within(input, cursor, maximum, 2U)
        && cursor[0] == '0'
        && open_cfw_scan_lower((unsigned char)cursor[1]) == 'x') {
        const char *hex_start = cursor;
        int fractional_digits = 0;
        cursor += 2;
        while (open_cfw_scan_within(input, cursor, maximum, 1U)
               && open_cfw_scan_hex_value((unsigned char)*cursor) >= 0) {
            value = value * 16.0
                + (double)open_cfw_scan_hex_value((unsigned char)*cursor++);
            ++digits;
        }
        if (open_cfw_scan_within(input, cursor, maximum, 1U)
            && *cursor == '.') {
            ++cursor;
            while (open_cfw_scan_within(input, cursor, maximum, 1U)
                   && open_cfw_scan_hex_value((unsigned char)*cursor) >= 0) {
                value = value * 16.0
                    + (double)open_cfw_scan_hex_value((unsigned char)*cursor++);
                ++fractional_digits;
                ++digits;
            }
        }
        if (digits == 0) {
            cursor = hex_start + 1;
            value = 0.0;
            digits = 1;
        } else {
            exponent = -4 * fractional_digits;
            if (open_cfw_scan_within(input, cursor, maximum, 1U)
                && open_cfw_scan_lower((unsigned char)*cursor) == 'p') {
                const char *mark = cursor++;
                int exponent_negative = 0;
                int exponent_digits = 0;
                int parsed = 0;
                if (open_cfw_scan_within(input, cursor, maximum, 1U)
                    && (*cursor == '+' || *cursor == '-')) {
                    exponent_negative = *cursor == '-';
                    ++cursor;
                }
                while (open_cfw_scan_within(input, cursor, maximum, 1U)
                       && open_cfw_scan_digit((unsigned char)*cursor)) {
                    if (parsed < 100000000) {
                        parsed = parsed * 10 + (*cursor - '0');
                    }
                    ++cursor;
                    ++exponent_digits;
                }
                if (exponent_digits == 0) {
                    cursor = mark;
                } else {
                    exponent += exponent_negative ? -parsed : parsed;
                }
            }
            value = open_cfw_scan_scale(value, 2U, exponent);
        }
    } else {
        int fractional_digits = 0;
        while (open_cfw_scan_within(input, cursor, maximum, 1U)
               && open_cfw_scan_digit((unsigned char)*cursor)) {
            value = value * 10.0 + (double)(*cursor++ - '0');
            ++digits;
        }
        if (open_cfw_scan_within(input, cursor, maximum, 1U)
            && *cursor == '.') {
            ++cursor;
            while (open_cfw_scan_within(input, cursor, maximum, 1U)
                   && open_cfw_scan_digit((unsigned char)*cursor)) {
                value = value * 10.0 + (double)(*cursor++ - '0');
                ++fractional_digits;
                ++digits;
            }
        }
        if (digits == 0) {
            cursor = number_start;
            goto no_conversion;
        }
        exponent = -fractional_digits;
        if (open_cfw_scan_within(input, cursor, maximum, 1U)
            && open_cfw_scan_lower((unsigned char)*cursor) == 'e') {
            const char *mark = cursor++;
            int exponent_negative = 0;
            int exponent_digits = 0;
            int parsed = 0;
            if (open_cfw_scan_within(input, cursor, maximum, 1U)
                && (*cursor == '+' || *cursor == '-')) {
                exponent_negative = *cursor == '-';
                ++cursor;
            }
            while (open_cfw_scan_within(input, cursor, maximum, 1U)
                   && open_cfw_scan_digit((unsigned char)*cursor)) {
                if (parsed < 100000000) {
                    parsed = parsed * 10 + (*cursor - '0');
                }
                ++cursor;
                ++exponent_digits;
            }
            if (exponent_digits == 0) {
                cursor = mark;
            } else {
                exponent += exponent_negative ? -parsed : parsed;
            }
        }
        value = open_cfw_scan_scale(value, 10U, exponent);
    }

done:
    if (end != (const char **)0) {
        *end = cursor;
    }
    return negative ? -value : value;

no_conversion:
    if (end != (const char **)0) {
        *end = input;
    }
    return 0.0;
}

double open_cfw_runtime_strtod(const char *input, const char **end)
{
    return open_cfw_runtime_strtod_bounded(input, ~0U, end);
}

int open_cfw_runtime_scanset_match(
    const unsigned char *table,
    unsigned int table_bytes,
    unsigned int character
)
{
    unsigned int remaining = table_bytes;
    unsigned int value = character & 0xFFU;

    while (remaining >= 3U) {
        if (table[1] == '-') {
            if (value >= table[0] && value <= table[2]) {
                return 1;
            }
            table += 3;
            remaining -= 3U;
        } else {
            if (value == *table) {
                return 1;
            }
            ++table;
            --remaining;
        }
    }
    while (remaining-- != 0U) {
        if (value == *table++) {
            return 1;
        }
    }
    return 0;
}

static unsigned long long open_cfw_scan_unsigned(
    const char **input,
    unsigned int width,
    unsigned int base,
    int *negative,
    int *converted
)
{
    const char *cursor = *input;
    unsigned long long result = 0U;
    unsigned int used = 0U;

    *negative = 0;
    *converted = 0;
    if (used < width && (*cursor == '+' || *cursor == '-')) {
        *negative = *cursor == '-';
        ++cursor;
        ++used;
    }
    if (base == 0U) {
        base = 10U;
        if (used < width && *cursor == '0') {
            base = 8U;
            if (used + 1U < width && open_cfw_scan_lower((unsigned char)cursor[1]) == 'x'
                && open_cfw_scan_hex_value((unsigned char)cursor[2]) >= 0) {
                base = 16U;
                cursor += 2;
                used += 2U;
            }
        }
    } else if (base == 16U && used + 1U < width && cursor[0] == '0'
               && open_cfw_scan_lower((unsigned char)cursor[1]) == 'x') {
        cursor += 2;
        used += 2U;
    }
    while (used < width) {
        int digit = open_cfw_scan_hex_value((unsigned char)*cursor);
        if (digit < 0 || (unsigned int)digit >= base) {
            break;
        }
        result = result * base + (unsigned int)digit;
        ++cursor;
        ++used;
        *converted = 1;
    }
    if (*converted != 0) {
        *input = cursor;
    }
    return result;
}

static __attribute__((always_inline)) inline void open_cfw_scan_store_signed(
    va_list *arguments,
    enum open_cfw_scan_length length,
    long long value
)
{
    switch (length) {
    case OPEN_CFW_SCAN_HH: *va_arg(*arguments, signed char *) = (signed char)value; break;
    case OPEN_CFW_SCAN_H: *va_arg(*arguments, short *) = (short)value; break;
    case OPEN_CFW_SCAN_L: *va_arg(*arguments, long *) = (long)value; break;
    case OPEN_CFW_SCAN_LL: *va_arg(*arguments, long long *) = value; break;
    case OPEN_CFW_SCAN_J: *va_arg(*arguments, intmax_t *) = (intmax_t)value; break;
    case OPEN_CFW_SCAN_Z: *va_arg(*arguments, ptrdiff_t *) = (ptrdiff_t)value; break;
    case OPEN_CFW_SCAN_T: *va_arg(*arguments, ptrdiff_t *) = (ptrdiff_t)value; break;
    default: *va_arg(*arguments, int *) = (int)value; break;
    }
}

static __attribute__((always_inline)) inline void open_cfw_scan_store_unsigned(
    va_list *arguments,
    enum open_cfw_scan_length length,
    unsigned long long value
)
{
    switch (length) {
    case OPEN_CFW_SCAN_HH: *va_arg(*arguments, unsigned char *) = (unsigned char)value; break;
    case OPEN_CFW_SCAN_H: *va_arg(*arguments, unsigned short *) = (unsigned short)value; break;
    case OPEN_CFW_SCAN_L: *va_arg(*arguments, unsigned long *) = (unsigned long)value; break;
    case OPEN_CFW_SCAN_LL: *va_arg(*arguments, unsigned long long *) = value; break;
    case OPEN_CFW_SCAN_J: *va_arg(*arguments, uintmax_t *) = (uintmax_t)value; break;
    case OPEN_CFW_SCAN_Z: *va_arg(*arguments, size_t *) = (size_t)value; break;
    case OPEN_CFW_SCAN_T: *va_arg(*arguments, uintptr_t *) = (uintptr_t)value; break;
    default: *va_arg(*arguments, unsigned int *) = (unsigned int)value; break;
    }
}

int open_cfw_runtime_vsscanf(
    const char *input,
    const char *format,
    va_list supplied_arguments
)
{
    const char *cursor = input;
    unsigned int assigned = 0U;
    va_list arguments;

    va_copy(arguments, supplied_arguments);
    while (*format != '\0') {
        unsigned int suppress = 0U;
        unsigned int width = ~0U;
        enum open_cfw_scan_length length = OPEN_CFW_SCAN_DEFAULT;
        unsigned int conversion;

        if (open_cfw_scan_space((unsigned char)*format)) {
            do { ++format; } while (open_cfw_scan_space((unsigned char)*format));
            while (open_cfw_scan_space((unsigned char)*cursor)) { ++cursor; }
            continue;
        }
        if (*format != '%') {
            if (*cursor == '\0' || *cursor != *format) { break; }
            ++cursor;
            ++format;
            continue;
        }
        ++format;
        if (*format == '%') {
            if (*cursor != '%') { break; }
            ++cursor;
            ++format;
            continue;
        }
        if (*format == '*') { suppress = 1U; ++format; }
        if (open_cfw_scan_digit((unsigned char)*format)) {
            width = 0U;
            do { width = width * 10U + (unsigned int)(*format++ - '0'); }
            while (open_cfw_scan_digit((unsigned char)*format));
        }
        if (*format == 'h') {
            length = *++format == 'h' ? (++format, OPEN_CFW_SCAN_HH) : OPEN_CFW_SCAN_H;
        } else if (*format == 'l') {
            length = *++format == 'l' ? (++format, OPEN_CFW_SCAN_LL) : OPEN_CFW_SCAN_L;
        } else if (*format == 'j') { length = OPEN_CFW_SCAN_J; ++format;
        } else if (*format == 'z') { length = OPEN_CFW_SCAN_Z; ++format;
        } else if (*format == 't') { length = OPEN_CFW_SCAN_T; ++format;
        } else if (*format == 'L') { length = OPEN_CFW_SCAN_CAP_L; ++format; }
        conversion = (unsigned char)*format++;

        if (conversion != 'c' && conversion != '[' && conversion != 'n') {
            while (open_cfw_scan_space((unsigned char)*cursor)) { ++cursor; }
        }
        if (conversion == 'n') {
            if (suppress == 0U) {
                open_cfw_scan_store_signed(&arguments, length, (long long)(cursor - input));
            }
            continue;
        }
        if (conversion == 'c') {
            unsigned int count = width == ~0U ? 1U : width;
            const char *start = cursor;
            while (count != 0U && *cursor != '\0') { ++cursor; --count; }
            if (cursor == start || count != 0U) { break; }
            if (suppress == 0U) {
                char *destination = va_arg(arguments, char *);
                while (start != cursor) { *destination++ = *start++; }
                ++assigned;
            }
            continue;
        }
        if (conversion == 's') {
            const char *start = cursor;
            unsigned int count = width;
            while (count != 0U && *cursor != '\0'
                   && !open_cfw_scan_space((unsigned char)*cursor)) {
                ++cursor;
                --count;
            }
            if (cursor == start) { break; }
            if (suppress == 0U) {
                char *destination = va_arg(arguments, char *);
                while (start != cursor) { *destination++ = *start++; }
                *destination = '\0';
                ++assigned;
            }
            continue;
        }
        if (conversion == '[') {
            const unsigned char *table;
            unsigned int invert = 0U;
            unsigned int table_bytes;
            const char *start = cursor;
            const char *table_start = format;
            unsigned int count = width;
            if (*format == '^') { invert = 1U; table_start = ++format; }
            if (*format == ']') { ++format; }
            while (*format != '\0' && *format != ']') { ++format; }
            if (*format != ']') { break; }
            table = (const unsigned char *)table_start;
            table_bytes = (unsigned int)(format - table_start);
            ++format;
            while (count != 0U && *cursor != '\0'
                   && ((unsigned int)open_cfw_runtime_scanset_match(
                       table, table_bytes, (unsigned char)*cursor) ^ invert) != 0U) {
                ++cursor;
                --count;
            }
            if (cursor == start) { break; }
            if (suppress == 0U) {
                char *destination = va_arg(arguments, char *);
                while (start != cursor) { *destination++ = *start++; }
                *destination = '\0';
                ++assigned;
            }
            continue;
        }
        if (conversion == 'f' || conversion == 'F' || conversion == 'e'
            || conversion == 'E' || conversion == 'g' || conversion == 'G'
            || conversion == 'a' || conversion == 'A') {
            const char *end;
            double value = open_cfw_runtime_strtod_bounded(cursor, width, &end);
            if (end == cursor) { break; }
            cursor = end;
            if (suppress == 0U) {
                if (length == OPEN_CFW_SCAN_CAP_L) {
                    *va_arg(arguments, long double *) = (long double)value;
                } else if (length == OPEN_CFW_SCAN_L) {
                    *va_arg(arguments, double *) = value;
                } else {
                    *va_arg(arguments, float *) = (float)value;
                }
                ++assigned;
            }
            continue;
        }
        if (conversion == 'd' || conversion == 'i' || conversion == 'u'
            || conversion == 'o' || conversion == 'x' || conversion == 'X'
            || conversion == 'p') {
            unsigned int base = conversion == 'i' ? 0U
                : conversion == 'o' ? 8U
                : (conversion == 'x' || conversion == 'X' || conversion == 'p') ? 16U
                : 10U;
            int negative;
            int converted;
            unsigned long long value = open_cfw_scan_unsigned(
                &cursor, width, base, &negative, &converted
            );
            if (converted == 0) { break; }
            if (suppress == 0U) {
                if (conversion == 'p') {
                    *va_arg(arguments, void **) = (void *)(uintptr_t)value;
                } else if (conversion == 'd' || conversion == 'i') {
                    long long signed_value = negative
                        ? -(long long)value : (long long)value;
                    open_cfw_scan_store_signed(&arguments, length, signed_value);
                } else {
                    if (negative) { value = 0U - value; }
                    open_cfw_scan_store_unsigned(&arguments, length, value);
                }
                ++assigned;
            }
            continue;
        }
        break;
    }
    va_end(arguments);
    return (int)assigned;
}

int open_cfw_runtime_sscanf(const char *input, const char *format, ...)
{
    va_list arguments;
    int result;

    va_start(arguments, format);
    result = open_cfw_runtime_vsscanf(input, format, arguments);
    va_end(arguments);
    return result;
}

typedef unsigned int (*open_cfw_runtime_iar_scan_reader)(
    const unsigned char **cursor,
    unsigned int value,
    int read
);

/*
 * Exact soft-PCS ingress used by the sole stock scanf-core caller.  The IAR
 * wrapper passes a pointer to the first variadic argument in its fourth
 * parameter.  Clang's AAPCS va_list is the same single __ap cursor, so the
 * source-owned scanner can consume it without retaining any DLIB helper.
 */
#if defined(__arm__) || defined(__thumb__)
__attribute__((used, noinline, pcs("aapcs")))
int open_cfw_runtime_iar_scanf_core(
    open_cfw_runtime_iar_scan_reader reader,
    const unsigned char **cursor,
    const char *format,
    void **argument_cursor,
    int secure
)
{
    __builtin_va_list arguments;

    (void)reader;
    (void)secure;
    arguments.__ap = *argument_cursor;
    return open_cfw_runtime_vsscanf((const char *)*cursor, format, arguments);
}
#endif
