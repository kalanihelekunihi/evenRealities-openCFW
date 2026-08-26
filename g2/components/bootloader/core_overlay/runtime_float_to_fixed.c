/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_numeric.h"

__attribute__((used, noinline))
OPEN_CFW_BOOTLOADER_FLOAT_ABI
int32_t open_cfw_bootloader_float_to_fixed(
    char *output,
    int32_t precision,
    float value
)
{
    union {
        float number;
        uint32_t bits;
    } decoded = { value };
    const uint32_t capacity = *(const uint32_t *)(const void *)output;
    const uint32_t magnitude = decoded.bits & UINT32_C(0x7FFFFFFF);
    char *cursor = output;
    uint32_t mantissa;
    uint32_t fraction = 0U;
    int32_t exponent;
    int32_t integer;

    if (capacity < 4U) {
        return -3;
    }
    if (magnitude == 0U) {
        output[0] = '0';
        output[1] = '.';
        output[2] = '0';
        output[3] = '\0';
        return 3;
    }

    exponent = (int32_t)((decoded.bits >> 23U) & 0xFFU) - 127;
    mantissa = (decoded.bits & UINT32_C(0x007FFFFF))
        | UINT32_C(0x00800000);
    if (exponent >= 31) {
        return -2;
    }
    if (exponent < -23) {
        return -1;
    }
    if (exponent >= 23) {
        integer = (int32_t)(mantissa << (uint32_t)(exponent - 23));
    }
    else if (exponent >= 0) {
        integer = (int32_t)(mantissa >> (uint32_t)(23 - exponent));
        fraction = (mantissa << (uint32_t)(exponent + 1))
            & UINT32_C(0x00FFFFFF);
    }
    else {
        integer = 0;
        fraction = (mantissa & UINT32_C(0x00FFFFFF))
            >> (uint32_t)(-(exponent + 1));
    }

    if ((decoded.bits & UINT32_C(0x80000000)) != 0U) {
        *cursor++ = '-';
    }
    if (integer == 0) {
        *cursor++ = '0';
    }
    else {
        uint64_t decimal;
        if (integer < 1) {
            *cursor++ = '-';
            decimal = (uint64_t)(int64_t)(int32_t)(0U - (uint32_t)integer);
        }
        else {
            decimal = (uint64_t)(int64_t)integer;
        }
        (void)open_cfw_bootloader_u64_to_dec(decimal, cursor);
        while (*cursor != '\0') {
            ++cursor;
        }
    }
    *cursor++ = '.';

    if (fraction == 0U) {
        *cursor++ = '0';
    }
    else {
        const uint32_t used = (uint32_t)(cursor - output);
        int32_t available = (int32_t)(capacity - used - 1U);
        int32_t emitted = 0;
        if (precision > available) {
            precision = available;
        }
        while (emitted < precision) {
            fraction *= 10U;
            *cursor++ = (char)('0' + (fraction >> 24U));
            fraction &= UINT32_C(0x00FFFFFF);
            ++emitted;
        }
        fraction *= 10U;
        if ((fraction >> 24U) >= 5U) {
            char *round = cursor - 1;
            while (round >= output) {
                if (*round == '.') {
                    --round;
                }
                else if (*round == '9') {
                    *round-- = '0';
                }
                else {
                    ++*round;
                    break;
                }
            }
        }
    }
    *cursor = '\0';
    return (int32_t)(cursor - output);
}
