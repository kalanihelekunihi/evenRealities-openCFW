/*
 * SPDX-License-Identifier: MIT
 *
 * Small, allocation-free ISO C and IEC 60559 scalar providers used only by
 * the production-excluded Cortex-M55 source-admission harness.  The routines
 * avoid compiler builtins so their provider closure remains inspectable.
 */

#include "runtime_target_scalar_candidate.h"

typedef __UINT8_TYPE__ open_cfw_target_u8;
typedef __UINT32_TYPE__ open_cfw_target_u32;
typedef __UINTPTR_TYPE__ open_cfw_target_uintptr;

typedef union open_cfw_target_float_bits {
    float value;
    open_cfw_target_u32 bits;
} open_cfw_target_float_bits;

enum {
    OPEN_CFW_FLOAT_SIGN = 0x80000000U,
    OPEN_CFW_FLOAT_ABS = 0x7fffffffU,
    OPEN_CFW_FLOAT_EXP = 0x7f800000U,
    OPEN_CFW_FLOAT_FRAC = 0x007fffffU,
    OPEN_CFW_FLOAT_QUIET = 0x00400000U,
};

void *open_cfw_target_memchr(const void *buffer, int value,
                             open_cfw_target_size count)
{
    const open_cfw_target_u8 *input = (const open_cfw_target_u8 *)buffer;
    open_cfw_target_u8 needle = (open_cfw_target_u8)value;

    while (count != 0U) {
        if (*input == needle)
            return (void *)input;
        ++input;
        --count;
    }
    return (void *)0;
}

int open_cfw_target_memcmp(const void *first, const void *second,
                          open_cfw_target_size count)
{
    const open_cfw_target_u8 *left = (const open_cfw_target_u8 *)first;
    const open_cfw_target_u8 *right = (const open_cfw_target_u8 *)second;

    while (count != 0U) {
        if (*left != *right)
            return (int)*left - (int)*right;
        ++left;
        ++right;
        --count;
    }
    return 0;
}

void *open_cfw_target_memcpy(void *destination, const void *source,
                            open_cfw_target_size count)
{
    open_cfw_target_u8 *output = (open_cfw_target_u8 *)destination;
    const open_cfw_target_u8 *input = (const open_cfw_target_u8 *)source;
    open_cfw_target_size index;

    for (index = 0U; index < count; ++index)
        output[index] = input[index];
    return destination;
}

void *open_cfw_target_memmove(void *destination, const void *source,
                             open_cfw_target_size count)
{
    open_cfw_target_u8 *output = (open_cfw_target_u8 *)destination;
    const open_cfw_target_u8 *input = (const open_cfw_target_u8 *)source;
    open_cfw_target_uintptr output_address = (open_cfw_target_uintptr)output;
    open_cfw_target_uintptr input_address = (open_cfw_target_uintptr)input;

    if (output_address <= input_address
        || output_address - input_address >= count) {
        open_cfw_target_size index;
        for (index = 0U; index < count; ++index)
            output[index] = input[index];
    } else {
        while (count != 0U) {
            --count;
            output[count] = input[count];
        }
    }
    return destination;
}

void *open_cfw_target_memset(void *destination, int value,
                            open_cfw_target_size count)
{
    open_cfw_target_u8 *output = (open_cfw_target_u8 *)destination;
    open_cfw_target_u8 byte = (open_cfw_target_u8)value;

    while (count != 0U) {
        *output++ = byte;
        --count;
    }
    return destination;
}

open_cfw_target_size open_cfw_target_strlen(const char *text)
{
    const char *cursor = text;
    while (*cursor != '\0')
        ++cursor;
    return (open_cfw_target_size)(cursor - text);
}

char *open_cfw_target_strcpy(char *destination, const char *source)
{
    char *output = destination;
    do {
        *output++ = *source;
    } while (*source++ != '\0');
    return destination;
}

char *open_cfw_target_strncpy(char *destination, const char *source,
                              open_cfw_target_size count)
{
    open_cfw_target_size index = 0U;
    while (index < count && source[index] != '\0') {
        destination[index] = source[index];
        ++index;
    }
    while (index < count)
        destination[index++] = '\0';
    return destination;
}

char *open_cfw_target_strcat(char *destination, const char *source)
{
    (void)open_cfw_target_strcpy(
        destination + open_cfw_target_strlen(destination), source
    );
    return destination;
}

int open_cfw_target_strcmp(const char *first, const char *second)
{
    while (*first != '\0' && *first == *second) {
        ++first;
        ++second;
    }
    return (int)(open_cfw_target_u8)*first
         - (int)(open_cfw_target_u8)*second;
}

int open_cfw_target_strncmp(const char *first, const char *second,
                           open_cfw_target_size count)
{
    while (count != 0U) {
        open_cfw_target_u8 left = (open_cfw_target_u8)*first++;
        open_cfw_target_u8 right = (open_cfw_target_u8)*second++;
        if (left != right)
            return (int)left - (int)right;
        if (left == 0U)
            return 0;
        --count;
    }
    return 0;
}

char *open_cfw_target_strrchr(const char *text, int value)
{
    const char *match = (const char *)0;
    char needle = (char)value;
    do {
        if (*text == needle)
            match = text;
    } while (*text++ != '\0');
    return (char *)match;
}

char *open_cfw_target_strstr(const char *text, const char *needle)
{
    open_cfw_target_size needle_length = open_cfw_target_strlen(needle);
    if (needle_length == 0U)
        return (char *)text;
    while (*text != '\0') {
        if (*text == *needle
            && open_cfw_target_strncmp(text, needle, needle_length) == 0)
            return (char *)text;
        ++text;
    }
    return (char *)0;
}

static void open_cfw_target_swap(open_cfw_target_u8 *first,
                                 open_cfw_target_u8 *second,
                                 open_cfw_target_size width)
{
    while (width != 0U) {
        open_cfw_target_u8 temporary = *first;
        *first++ = *second;
        *second++ = temporary;
        --width;
    }
}

void open_cfw_target_qsort(
    void *base,
    open_cfw_target_size count,
    open_cfw_target_size width,
    int (*compare)(const void *, const void *)
)
{
    open_cfw_target_u8 *bytes = (open_cfw_target_u8 *)base;
    open_cfw_target_size outer;

    if (count < 2U || width == 0U)
        return;
    for (outer = 1U; outer < count; ++outer) {
        open_cfw_target_size inner = outer;
        while (inner != 0U
               && compare(bytes + inner * width,
                          bytes + (inner - 1U) * width) < 0) {
            open_cfw_target_swap(bytes + inner * width,
                                 bytes + (inner - 1U) * width, width);
            --inner;
        }
    }
}

static int open_cfw_target_is_nan_bits(open_cfw_target_u32 bits)
{
    return (bits & OPEN_CFW_FLOAT_ABS) > OPEN_CFW_FLOAT_EXP;
}

float open_cfw_target_fabsf(float value)
{
    open_cfw_target_float_bits converted = { value };
    converted.bits &= OPEN_CFW_FLOAT_ABS;
    return converted.value;
}

float open_cfw_target_truncf(float value)
{
    open_cfw_target_float_bits converted = { value };
    open_cfw_target_u32 exponent = (converted.bits >> 23U) & 0xffU;

    if (exponent < 127U) {
        converted.bits &= OPEN_CFW_FLOAT_SIGN;
    } else if (exponent < 150U) {
        open_cfw_target_u32 fractional_bits = 150U - exponent;
        converted.bits &= ~((1U << fractional_bits) - 1U);
    }
    return converted.value;
}

float open_cfw_target_floorf(float value)
{
    float integral = open_cfw_target_truncf(value);
    if (value < 0.0F && integral != value)
        integral -= 1.0F;
    return integral;
}

float open_cfw_target_roundf(float value)
{
    open_cfw_target_float_bits converted = { value };
    open_cfw_target_u32 magnitude = converted.bits & OPEN_CFW_FLOAT_ABS;
    open_cfw_target_u32 exponent = magnitude >> 23U;

    if (exponent < 126U) {
        converted.bits &= OPEN_CFW_FLOAT_SIGN;
    } else if (exponent == 126U) {
        converted.bits = (converted.bits & OPEN_CFW_FLOAT_SIGN) | 0x3f800000U;
    } else if (exponent < 150U) {
        open_cfw_target_u32 fractional_bits = 150U - exponent;
        open_cfw_target_u32 mask = (1U << fractional_bits) - 1U;
        open_cfw_target_u32 fraction = magnitude & mask;
        magnitude &= ~mask;
        if (fraction >= (1U << (fractional_bits - 1U)))
            magnitude += 1U << fractional_bits;
        converted.bits = (converted.bits & OPEN_CFW_FLOAT_SIGN) | magnitude;
    }
    return converted.value;
}

float open_cfw_target_fminf(float first, float second)
{
    open_cfw_target_float_bits left = { first };
    open_cfw_target_float_bits right = { second };
    if (open_cfw_target_is_nan_bits(left.bits))
        return second;
    if (open_cfw_target_is_nan_bits(right.bits))
        return first;
    if (first == second) {
        left.bits |= right.bits & OPEN_CFW_FLOAT_SIGN;
        return left.value;
    }
    return first < second ? first : second;
}

float open_cfw_target_fmaxf(float first, float second)
{
    open_cfw_target_float_bits left = { first };
    open_cfw_target_float_bits right = { second };
    if (open_cfw_target_is_nan_bits(left.bits))
        return second;
    if (open_cfw_target_is_nan_bits(right.bits))
        return first;
    if (first == second) {
        left.bits &= right.bits | OPEN_CFW_FLOAT_ABS;
        return left.value;
    }
    return first > second ? first : second;
}

float open_cfw_target_sqrtf(float value)
{
    open_cfw_target_float_bits converted = { value };
    if ((converted.bits & OPEN_CFW_FLOAT_SIGN) != 0U
        && (converted.bits & OPEN_CFW_FLOAT_ABS) != 0U) {
        converted.bits = OPEN_CFW_FLOAT_EXP | OPEN_CFW_FLOAT_QUIET;
        return converted.value;
    }
#if defined(__arm__) || defined(__thumb__)
    {
        float result;
        __asm__ volatile("vsqrt.f32 %0, %1" : "=t"(result) : "t"(value));
        return result;
    }
#else
    return __builtin_sqrtf(value);
#endif
}

#ifdef OPEN_CFW_TARGET_RUNTIME_EXPORT_NAMES

void *memchr(const void *buffer, int value, open_cfw_target_size count)
{ return open_cfw_target_memchr(buffer, value, count); }
int memcmp(const void *first, const void *second, open_cfw_target_size count)
{ return open_cfw_target_memcmp(first, second, count); }
void *memcpy(void *destination, const void *source, open_cfw_target_size count)
{ return open_cfw_target_memcpy(destination, source, count); }
void *memmove(void *destination, const void *source, open_cfw_target_size count)
{ return open_cfw_target_memmove(destination, source, count); }
void *memset(void *destination, int value, open_cfw_target_size count)
{ return open_cfw_target_memset(destination, value, count); }
char *strcat(char *destination, const char *source)
{ return open_cfw_target_strcat(destination, source); }
int strcmp(const char *first, const char *second)
{ return open_cfw_target_strcmp(first, second); }
char *strcpy(char *destination, const char *source)
{ return open_cfw_target_strcpy(destination, source); }
open_cfw_target_size strlen(const char *text)
{ return open_cfw_target_strlen(text); }
int strncmp(const char *first, const char *second, open_cfw_target_size count)
{ return open_cfw_target_strncmp(first, second, count); }
char *strncpy(char *destination, const char *source,
              open_cfw_target_size count)
{ return open_cfw_target_strncpy(destination, source, count); }
char *strrchr(const char *text, int value)
{ return open_cfw_target_strrchr(text, value); }
char *strstr(const char *text, const char *needle)
{ return open_cfw_target_strstr(text, needle); }
void qsort(void *base, open_cfw_target_size count, open_cfw_target_size width,
           int (*compare)(const void *, const void *))
{ open_cfw_target_qsort(base, count, width, compare); }
float fabsf(float value) { return open_cfw_target_fabsf(value); }
float floorf(float value) { return open_cfw_target_floorf(value); }
float fmaxf(float first, float second)
{ return open_cfw_target_fmaxf(first, second); }
float fminf(float first, float second)
{ return open_cfw_target_fminf(first, second); }
float roundf(float value) { return open_cfw_target_roundf(value); }
float sqrtf(float value) { return open_cfw_target_sqrtf(value); }
float truncf(float value) { return open_cfw_target_truncf(value); }

void __aeabi_memcpy4(void *destination, const void *source,
                     open_cfw_target_size count)
{ (void)open_cfw_target_memcpy(destination, source, count); }
void __aeabi_memclr(void *destination, open_cfw_target_size count)
{ (void)open_cfw_target_memset(destination, 0, count); }
void __aeabi_memclr4(void *destination, open_cfw_target_size count)
{ (void)open_cfw_target_memset(destination, 0, count); }

#endif
