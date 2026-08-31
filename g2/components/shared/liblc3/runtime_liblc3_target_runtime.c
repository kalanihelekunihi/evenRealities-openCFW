/* SPDX-License-Identifier: MIT */
/* Freestanding ISO-C/Arm-EABI scalar runtime for the admitted LC3 closure. */

#include "runtime_liblc3_target_runtime.h"

#define OPEN_CFW_RUNTIME __attribute__((used, noinline, visibility("default")))

typedef union {
    float value;
    unsigned int bits;
} open_cfw_liblc3_float_bits;

typedef __UINTPTR_TYPE__ open_cfw_liblc3_uintptr_t;

static void open_cfw_liblc3_clear(void *destination,
                                  open_cfw_liblc3_size_t size)
{
    unsigned char *output = (unsigned char *)destination;
    while (size != 0U) {
        *output++ = 0U;
        --size;
    }
}

OPEN_CFW_RUNTIME void __aeabi_memclr(void *destination,
                                     open_cfw_liblc3_size_t size)
{
    open_cfw_liblc3_clear(destination, size);
}

OPEN_CFW_RUNTIME void __aeabi_memclr4(void *destination,
                                      open_cfw_liblc3_size_t size)
{
    open_cfw_liblc3_clear(destination, size);
}

OPEN_CFW_RUNTIME void *memcpy(void *destination, const void *source,
                              open_cfw_liblc3_size_t size)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    void *result = destination;
    while (size != 0U) {
        *output++ = *input++;
        --size;
    }
    return result;
}

OPEN_CFW_RUNTIME void *memmove(void *destination, const void *source,
                               open_cfw_liblc3_size_t size)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    open_cfw_liblc3_uintptr_t output_address =
        (open_cfw_liblc3_uintptr_t)destination;
    open_cfw_liblc3_uintptr_t input_address =
        (open_cfw_liblc3_uintptr_t)source;
    void *result = destination;
    if (output_address <= input_address ||
        output_address - input_address >= size) {
        while (size != 0U) {
            *output++ = *input++;
            --size;
        }
    } else {
        output += size;
        input += size;
        while (size != 0U) {
            *--output = *--input;
            --size;
        }
    }
    return result;
}

OPEN_CFW_RUNTIME void *memset(void *destination, int value,
                              open_cfw_liblc3_size_t size)
{
    unsigned char *output = (unsigned char *)destination;
    void *result = destination;
    while (size != 0U) {
        *output++ = (unsigned char)value;
        --size;
    }
    return result;
}

OPEN_CFW_RUNTIME float fabsf(float value)
{
    open_cfw_liblc3_float_bits bits = {value};
    bits.bits &= 0x7FFFFFFFU;
    return bits.value;
}

OPEN_CFW_RUNTIME float truncf(float value)
{
    open_cfw_liblc3_float_bits bits = {value};
    unsigned int exponent = (bits.bits >> 23) & 0xFFU;
    if (exponent < 127U) {
        bits.bits &= 0x80000000U;
    } else if (exponent < 150U) {
        bits.bits &= ~((1U << (150U - exponent)) - 1U);
    }
    return bits.value;
}

OPEN_CFW_RUNTIME float floorf(float value)
{
    float integer = truncf(value);
    return value < integer ? integer - 1.0F : integer;
}

OPEN_CFW_RUNTIME float fmaxf(float first, float second)
{
    open_cfw_liblc3_float_bits left = {first};
    if (first != first) {
        return second;
    }
    if (second != second) {
        return first;
    }
    if (first == second) {
        return (left.bits & 0x80000000U) != 0U ? second : first;
    }
    return first > second ? first : second;
}

OPEN_CFW_RUNTIME float fminf(float first, float second)
{
    open_cfw_liblc3_float_bits left = {first};
    if (first != first) {
        return second;
    }
    if (second != second) {
        return first;
    }
    if (first == second) {
        return (left.bits & 0x80000000U) != 0U ? first : second;
    }
    return first < second ? first : second;
}
