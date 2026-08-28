/* SPDX-License-Identifier: MIT */
#include "string.h"

void *memcpy(void *restrict destination, const void *restrict source, size_t count)
{
    unsigned char *out = (unsigned char *)destination;
    const unsigned char *in = (const unsigned char *)source;
    size_t i;
    for (i = 0u; i < count; ++i) {
        out[i] = in[i];
    }
    return destination;
}

char *strcpy(char *restrict destination, const char *restrict source)
{
    size_t i = 0u;
    do {
        destination[i] = source[i];
    } while (source[i++] != '\0');
    return destination;
}

size_t strlen(const char *text)
{
    size_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}
