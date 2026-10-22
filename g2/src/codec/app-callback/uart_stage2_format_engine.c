/* SPDX-License-Identifier: MIT
 * C candidate for the outer UART stage-2 formatter at 0x10006b40.
 * Native jump tables at 0x10008b88/8d1c/8bcc/8e6c determine the grammar.
 * Numeric rendering 0x1000691c and bounded string length 0x10006350 are
 * separately typed lower bodies, not substituted with host libc.
 */
#include <stdarg.h>
#include <stdint.h>
#include <stddef.h>

extern char *gx8002_uart_stage2_format_number_691c(char *out,
    uint32_t low, uint32_t high, uint32_t base, int32_t width,
    int32_t precision, uint32_t flags);
/* Stock 0x10006350 (gx8002_stage2_strnlen) */
int32_t gx8002_uart_stage2_format_strlen_6350(const char *text,
                                                int32_t precision)
{
    int32_t size = 0;
    while (size != precision && text[size] != '\0') ++size;
    return size;
}

enum { F_ZERO = 1, F_SIGNED = 2, F_PLUS = 4, F_SPACE = 8,
       F_LEFT = 16, F_LOWER = 32, F_ALT = 64 };

static void spaces(char **out, int32_t count)
{
    while (count-- > 0) *(*out)++ = ' ';
}

int32_t gx8002_uart_stage2_format_engine_6b40(char *buffer,
                                                 const char *format,
                                                 va_list arguments)
{
    char *out = buffer;
    const char *p = format;
    while (*p) {
        if (*p != '%') { *out++ = *p++; continue; }
        const char *const percent = p++;
        uint32_t flags = 0;
        for (;;) {
            switch (*p) {
            case '0': flags |= F_ZERO; ++p; continue;
            case '-': flags |= F_LEFT; ++p; continue;
            case '+': flags |= F_PLUS; ++p; continue;
            case '#': flags |= F_ALT; ++p; continue;
            case ' ': flags |= F_SPACE; ++p; continue;
            default: break;
            }
            break;
        }
        int32_t width = -1;
        if (*p >= '0' && *p <= '9') {
            width = 0;
            while (*p >= '0' && *p <= '9') width = width * 10 + (*p++ - '0');
        } else if (*p == '*') {
            width = va_arg(arguments, int32_t);
            ++p;
            if (width < 0) { width = -width; flags |= F_LEFT; }
        }
        int32_t precision = -1;
        if (*p == '.') {
            ++p;
            precision = 0;
            if (*p == '*') {
                precision = va_arg(arguments, int32_t);
                if (precision < 0) precision = 0;
                ++p;
            } else {
                while (*p >= '0' && *p <= '9')
                    precision = precision * 10 + (*p++ - '0');
            }
        }
        int length = 0;
        if (*p == 'h') { length = 1; ++p; }
        else if (*p == 'l') { length = 2; ++p; if (*p == 'l') { length = 3; ++p; } }
        else if (*p == 'L' || *p == 'z' || *p == 'Z' || *p == 't')
            { length = 3; ++p; }
        const char conversion = *p;
        if (conversion == '\0') { *out++ = '%'; break; }
        ++p;

        if (conversion == '%') { *out++ = '%'; continue; }
        if (conversion == 'n') {
            uint32_t *const target = va_arg(arguments, uint32_t *);
            *target = (uint32_t)(out - buffer);
            continue;
        }
        if (conversion == 's') {
            const char *text = va_arg(arguments, const char *);
            if (text == NULL) text = "<NULL>";
            const int32_t size = gx8002_uart_stage2_format_strlen_6350(text,
                                                                          precision);
            if (!(flags & F_LEFT)) spaces(&out, width - size);
            for (int32_t i = 0; i < size; ++i) *out++ = text[i];
            if (flags & F_LEFT) spaces(&out, width - size);
            continue;
        }
        if (conversion == 'c') {
            const int32_t character = va_arg(arguments, int32_t);
            if (!(flags & F_LEFT)) spaces(&out, width - 1);
            *out++ = (char)character;
            if (flags & F_LEFT) spaces(&out, width - 1);
            continue;
        }
        uint32_t base = 10;
        switch (conversion) {
        case 'd': case 'i': flags |= F_SIGNED; break;
        case 'u': break;
        case 'o': base = 8; break;
        case 'x': base = 16; flags |= F_LOWER; break;
        case 'X': base = 16; break;
        case 'p':
            base = 16;
            flags |= F_LOWER | F_ALT;
            if (precision < 0) precision = 8;
            break;
        default:
            *out++ = '%';
            *out++ = conversion;
            (void)percent;
            continue;
        }
        uint32_t low;
        uint32_t high = 0;
        if (length == 3 && conversion != 'p') {
            const uint64_t value = va_arg(arguments, uint64_t);
            low = (uint32_t)value;
            high = (uint32_t)(value >> 32);
        } else {
            low = va_arg(arguments, uint32_t);
            if (length == 1) {
                low = flags & F_SIGNED ? (uint32_t)(int32_t)(int16_t)low
                                       : (uint16_t)low;
            }
            if (flags & F_SIGNED) high = (uint32_t)((int32_t)low >> 31);
        }
        out = gx8002_uart_stage2_format_number_691c(out, low, high,
                                                      base, width, precision,
                                                      flags);
    }
    *out = '\0';
    return (int32_t)(out - buffer);
}
