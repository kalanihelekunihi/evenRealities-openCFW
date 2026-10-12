/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020995c..0x102099c4. Stateful delimiter
 * scanner. The state cell is the stock SRAM literal 0x2002e934;
 * callers supply writable strings exactly as the native code expects.
 */
#include <stdint.h>

static char *volatile *const next_token =
    (char *volatile *)(uintptr_t)UINT32_C(0x2002e934);

static uint32_t is_delimiter(unsigned char value, const char *delimiters)
{
    for (const unsigned char *p = (const unsigned char *)delimiters;
         *p != 0u; ++p) {
        if (*p == value) return 1u;
    }
    return 0u;
}

char *gx8002_xip_strtok_1020995c(char *input, const char *delimiters)
{
    char *cursor = input != (void *)0 ? input : *next_token;
    if (cursor == (void *)0) return (void *)0;
    while (*cursor != '\0' &&
           is_delimiter((unsigned char)*cursor, delimiters)) ++cursor;
    if (*cursor == '\0') {
        *next_token = (void *)0;
        return (void *)0;
    }
    char *const token = cursor;
    ++cursor;
    while (*cursor != '\0' &&
           !is_delimiter((unsigned char)*cursor, delimiters)) ++cursor;
    if (*cursor != '\0') {
        *cursor = '\0';
        *next_token = cursor + 1;
    } else {
        *next_token = (void *)0;
    }
    return token;
}
