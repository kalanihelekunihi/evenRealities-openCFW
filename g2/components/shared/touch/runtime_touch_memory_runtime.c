/*
 * SPDX-License-Identifier: MIT
 *
 * Minimal ARM EABI memory helpers for the freestanding Touch image.
 */
#include <stddef.h>
#include <stdint.h>

void *__aeabi_memset(void *destination, size_t size, int value)
{
    uint8_t *bytes = destination;
    size_t index;
    for (index = 0U; index < size; ++index) {
        bytes[index] = (uint8_t)value;
    }
    return destination;
}

void *__aeabi_memset4(void *destination, size_t size, int value)
{
    return __aeabi_memset(destination, size, value);
}

void *__aeabi_memclr(void *destination, size_t size)
{
    return __aeabi_memset(destination, size, 0);
}

void *__aeabi_memclr4(void *destination, size_t size)
{
    return __aeabi_memset(destination, size, 0);
}

void *__aeabi_memcpy(void *destination, const void *source, size_t size)
{
    uint8_t *output = destination;
    const uint8_t *input = source;
    size_t index;
    for (index = 0U; index < size; ++index) {
        output[index] = input[index];
    }
    return destination;
}

void *__aeabi_memcpy4(void *destination, const void *source, size_t size)
{
    return __aeabi_memcpy(destination, source, size);
}

void *__aeabi_memmove(void *destination, const void *source, size_t size)
{
    uint8_t *output = destination;
    const uint8_t *input = source;
    if (output < input) {
        return __aeabi_memcpy(destination, source, size);
    }
    while (size != 0U) {
        --size;
        output[size] = input[size];
    }
    return destination;
}
