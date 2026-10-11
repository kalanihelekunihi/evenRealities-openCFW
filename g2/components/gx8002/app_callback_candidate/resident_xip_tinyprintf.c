/*
 * Derived from NationalChip LVP utility/libc/tinyprintf.c (BSD option).
 * Copyright (c) 2004,2012 Kustaa Nyholm / SpareTimeLabs.
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided the copyright notice, these
 * conditions, and the following disclaimer are retained in source and
 * reproduced in binary documentation. Neither the authors nor contributors
 * may endorse derived products without prior written permission.
 * THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTY. THE COPYRIGHT HOLDERS AND CONTRIBUTORS ARE NOT LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES ARISING FROM ITS USE, EVEN IF ADVISED OF THE POSSIBILITY.
 *
 * Native provenance: image-A XIP 0x10206920-0x10206c24 and 0x10206c70.
 * The formatter's format cases and helper flow match the pinned upstream
 * source; the output leaf calls the real resident console provider.
 */
#include <stdarg.h>
#include <stdint.h>

extern void gx8002_xip_console_putc_102037f0(uint32_t character);

struct gx8002_tfp_param {
    int width;
    char lz;
    char sign;
    char alt;
    char base;
    char uc;
    char *bf;
};

static void gx8002_tfp_ui2a(uint32_t num, struct gx8002_tfp_param *p)
{
    uint32_t divisor = 1;
    char *out = p->bf;
    int written = 0;
    while (num / divisor >= (uint32_t)p->base) divisor *= (uint32_t)p->base;
    while (divisor != 0) {
        uint32_t digit = num / divisor;
        num %= divisor;
        divisor /= (uint32_t)p->base;
        if (written || digit != 0 || divisor == 0) {
            *out++ = (char)(digit + (digit < 10 ? '0' : (p->uc ? 'A' : 'a') - 10));
            ++written;
        }
    }
    *out = 0;
}

static int gx8002_tfp_digit(char character)
{
    if (character >= '0' && character <= '9') return character - '0';
    if (character >= 'a' && character <= 'f') return character - 'a' + 10;
    if (character >= 'A' && character <= 'F') return character - 'A' + 10;
    return -1;
}

static char gx8002_tfp_parse_width(char character, const char **source,
                                   int base, int *number)
{
    const char *cursor = *source;
    int result = 0;
    int digit;
    while ((digit = gx8002_tfp_digit(character)) >= 0) {
        /* Preserve the pinned formatter's strict > test. */
        if (digit > base) break;
        result = result * base + digit;
        character = *cursor++;
    }
    *source = cursor;
    *number = result;
    return character;
}

static uint32_t gx8002_tfp_putf(void *stream, char character)
{
    (void)stream;
    gx8002_xip_console_putc_102037f0((uint8_t)character);
    /* Stock fputc at 0x10206c70 returns zero after the UART call. */
    return 1;
}

static uint32_t gx8002_tfp_putchw(void *stream, struct gx8002_tfp_param *p)
{
    uint32_t written = 0;
    char character;
    int filling = p->width;
    char *cursor = p->bf;
    while (*cursor++ && filling > 0) --filling;
    if (p->sign) --filling;
    if (p->alt && p->base == 16) filling -= 2;
    else if (p->alt && p->base == 8) --filling;
    if (!p->lz) while (filling-- > 0) written += gx8002_tfp_putf(stream, ' ');
    if (p->sign) written += gx8002_tfp_putf(stream, p->sign);
    if (p->alt && p->base == 16) {
        written += gx8002_tfp_putf(stream, '0');
        written += gx8002_tfp_putf(stream, p->uc ? 'X' : 'x');
    } else if (p->alt && p->base == 8) {
        written += gx8002_tfp_putf(stream, '0');
    }
    if (p->lz) while (filling-- > 0) written += gx8002_tfp_putf(stream, '0');
    cursor = p->bf;
    while ((character = *cursor++) != 0) written += gx8002_tfp_putf(stream, character);
    return written;
}

uint32_t gx8002_xip_tfp_format_10206a84(void *stream, const char *format,
                                           va_list arguments)
{
    uint32_t written = 0;
    char buffer[12];
    struct gx8002_tfp_param parameter;
    parameter.bf = buffer;
    char character;
    while ((character = *format++) != 0) {
        if (character != '%') {
            written += gx8002_tfp_putf(stream, character);
            continue;
        }
        parameter.lz = 0;
        parameter.alt = 0;
        parameter.width = 0;
        parameter.sign = 0;
        while ((character = *format++) != 0) {
            if (character == '0') { parameter.lz = 1; continue; }
            if (character == '#') { parameter.alt = 1; continue; }
            break;
        }
        if (character >= '0' && character <= '9')
            character = gx8002_tfp_parse_width(character, &format, 10,
                                                &parameter.width);
        if (character == 'l') character = *format++;
        if (character == 0) break;
        switch (character) {
        case 'u': case 'd': case 'i': case 'x': case 'X': case 'o': {
            uint32_t value = va_arg(arguments, uint32_t);
            parameter.base = (character == 'x' || character == 'X') ? 16 :
                             (character == 'o') ? 8 : 10;
            if (character == 'x' || character == 'X')
                parameter.uc = (character == 'X');
            if ((character == 'd' || character == 'i') && (int32_t)value < 0) {
                value = 0u - value;
                parameter.sign = '-';
            }
            gx8002_tfp_ui2a(value, &parameter);
            written += gx8002_tfp_putchw(stream, &parameter);
            break;
        }
        case 'c':
            written += gx8002_tfp_putf(stream, (char)va_arg(arguments, int));
            break;
        case 's':
            parameter.bf = va_arg(arguments, char *);
            written += gx8002_tfp_putchw(stream, &parameter);
            parameter.bf = buffer;
            break;
        case '%':
            written += gx8002_tfp_putf(stream, '%');
            break;
        default:
            break;
        }
    }
    return written;
}
