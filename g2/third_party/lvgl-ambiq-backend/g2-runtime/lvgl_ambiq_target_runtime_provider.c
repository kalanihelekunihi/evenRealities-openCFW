/* SPDX-License-Identifier: MIT */
/*
 * Allocation-free target runtime boundary for the isolated Ambiq draw link.
 * The conversion algorithms follow the bit decomposition used by LLVM
 * compiler-rt fixdfdi/fixunssfdi while defining saturating hostile behavior.
 */

#include "lvgl_ambiq_target_runtime_provider.h"

#include <stdbool.h>
#include <limits.h>

typedef union open_cfw_double_bits {
    double value;
    uint64_t bits;
} open_cfw_double_bits;

typedef union open_cfw_float_bits {
    float value;
    uint32_t bits;
} open_cfw_float_bits;

static void * copy_bytes(void * destination, const void * source, size_t length)
{
    volatile uint8_t * output = (volatile uint8_t *)destination;
    const volatile uint8_t * input = (const volatile uint8_t *)source;
    void * original = destination;

    if(length == 0U) return original;
    if(output == NULL || input == NULL) return original;
    while(length-- != 0U) *output++ = *input++;
    return original;
}

void * memcpy(void * destination, const void * source, size_t length)
{
    return copy_bytes(destination, source, length);
}

void * memset(void * destination, int value, size_t length)
{
    volatile uint8_t * output = (volatile uint8_t *)destination;
    void * original = destination;

    if(length == 0U) return original;
    if(output == NULL) return original;
    while(length-- != 0U) *output++ = (uint8_t)value;
    return original;
}

void __aeabi_memcpy4(void * destination, const void * source, size_t length)
{
    (void)copy_bytes(destination, source, length);
}

OPEN_CFW_AEABI_BASE_PCS int64_t __aeabi_d2lz(double value)
{
    const open_cfw_double_bits converted = { .value = value };
    const uint64_t magnitude_bits = converted.bits & UINT64_C(0x7fffffffffffffff);
    const bool negative = (converted.bits >> 63U) != 0U;
    const uint64_t significand =
        (magnitude_bits & UINT64_C(0x000fffffffffffff)) |
        UINT64_C(0x0010000000000000);
    const int32_t exponent = (int32_t)(magnitude_bits >> 52U) - 1023;
    uint64_t magnitude;

    if(exponent < 0) return 0;
    if(exponent >= 63) return negative ? INT64_MIN : INT64_MAX;
    if(exponent < 52) magnitude = significand >> (52 - exponent);
    else magnitude = significand << (exponent - 52);
    return negative ? -(int64_t)magnitude : (int64_t)magnitude;
}

OPEN_CFW_AEABI_BASE_PCS uint64_t __aeabi_f2ulz(float value)
{
    const open_cfw_float_bits converted = { .value = value };
    const uint32_t magnitude_bits = converted.bits & UINT32_C(0x7fffffff);
    const uint32_t significand =
        (magnitude_bits & UINT32_C(0x007fffff)) | UINT32_C(0x00800000);
    const int32_t exponent = (int32_t)(magnitude_bits >> 23U) - 127;

    if((converted.bits >> 31U) != 0U || exponent < 0) return UINT64_C(0);
    if(exponent >= 64) return UINT64_MAX;
    if(exponent < 23) return (uint64_t)(significand >> (23 - exponent));
    return (uint64_t)significand << (exponent - 23);
}
