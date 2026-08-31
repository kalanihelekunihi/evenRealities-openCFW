/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Clean-room semantic candidates for the two reconstructible MetaWare
 * runtime islands retained by the G2 EM9305 application.  This code is
 * derived from standard library semantics and independently reviewed ABI
 * behavior, not from MetaWare source code.
 */

#include "runtime_metaware_helpers_candidate.h"

struct open_cfw_em9305_udivmod_result {
    uint64_t quotient;
    uint64_t remainder;
};

union open_cfw_em9305_u64_words {
    uint64_t value;
    struct {
        uint32_t low;
        uint32_t high;
    } words;
};

static uint64_t open_cfw_em9305_shift_left64_words(
    uint64_t value,
    uint32_t count
)
{
    union open_cfw_em9305_u64_words input = { value };
    union open_cfw_em9305_u64_words output = { 0u };

    count &= 63u;
    if (count == 0u) {
        return value;
    }
    if (count < 32u) {
        output.words.low = input.words.low << count;
        output.words.high = (input.words.high << count) |
            (input.words.low >> (32u - count));
    } else {
        output.words.high = input.words.low << (count - 32u);
    }
    return output.value;
}

static uint64_t open_cfw_em9305_shift_right64_words(
    uint64_t value,
    uint32_t count
)
{
    union open_cfw_em9305_u64_words input = { value };
    union open_cfw_em9305_u64_words output = { 0u };

    count &= 63u;
    if (count == 0u) {
        return value;
    }
    if (count < 32u) {
        output.words.low = (input.words.low >> count) |
            (input.words.high << (32u - count));
        output.words.high = input.words.high >> count;
    } else {
        output.words.low = input.words.high >> (count - 32u);
    }
    return output.value;
}

static struct open_cfw_em9305_udivmod_result
open_cfw_em9305_udivmod64(uint64_t dividend, uint64_t divisor)
{
    struct open_cfw_em9305_udivmod_result result = { 0u, 0u };
    uint32_t bit;

    if (divisor == 0u) {
        result.quotient = UINT64_MAX;
        result.remainder = dividend;
        return result;
    }

    for (bit = 64u; bit != 0u; --bit) {
        uint32_t shift = bit - 1u;
        uint64_t incoming = open_cfw_em9305_shift_right64_words(
            dividend, shift
        ) & 1u;
        uint64_t high = open_cfw_em9305_shift_right64_words(
            result.remainder, 63u
        );

        result.remainder = open_cfw_em9305_shift_left64_words(
            result.remainder, 1u
        ) | incoming;
        if (high != 0u || result.remainder >= divisor) {
            result.remainder -= divisor;
            result.quotient |= open_cfw_em9305_shift_left64_words(
                UINT64_C(1), shift
            );
        }
    }
    return result;
}

static uint64_t open_cfw_em9305_signed_magnitude(int64_t value)
{
    if (value >= 0) {
        return (uint64_t)value;
    }
    return (uint64_t)(-(value + 1)) + 1u;
}

void *open_cfw_em9305_metaware_memmove_candidate(
    void *destination,
    const void *source,
    size_t length
)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    uintptr_t output_address = (uintptr_t)destination;
    uintptr_t input_address = (uintptr_t)source;
    size_t index;

    if (output == input || length == 0u) {
        return destination;
    }
    if (
        output_address <= input_address ||
        output_address - input_address >= length
    ) {
        for (index = 0u; index < length; ++index) {
            output[index] = input[index];
        }
    } else {
        for (index = length; index != 0u; --index) {
            output[index - 1u] = input[index - 1u];
        }
    }
    return destination;
}

void *open_cfw_em9305_metaware_memcpy_candidate(
    void *destination,
    const void *source,
    size_t length
)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    size_t index;

    for (index = 0u; index < length; ++index) {
        output[index] = input[index];
    }
    return destination;
}

void *open_cfw_em9305_metaware_memset_candidate(
    void *destination,
    int value,
    size_t length
)
{
    unsigned char *output = (unsigned char *)destination;
    unsigned char byte = (unsigned char)value;
    size_t index;

    for (index = 0u; index < length; ++index) {
        output[index] = byte;
    }
    return destination;
}

uint64_t open_cfw_em9305_metaware_udiv64_candidate(
    uint64_t dividend,
    uint64_t divisor
)
{
    return open_cfw_em9305_udivmod64(dividend, divisor).quotient;
}

int64_t open_cfw_em9305_metaware_sdiv64_candidate(
    int64_t dividend,
    int64_t divisor
)
{
    uint64_t quotient = open_cfw_em9305_udivmod64(
        open_cfw_em9305_signed_magnitude(dividend),
        open_cfw_em9305_signed_magnitude(divisor)
    ).quotient;
    uint32_t negative = (uint32_t)((dividend < 0) != (divisor < 0));

    if (negative != 0u) {
        if (quotient == UINT64_C(0x8000000000000000)) {
            return INT64_MIN;
        }
        if (quotient <= (uint64_t)INT64_MAX) {
            return -(int64_t)quotient;
        }
        /* The stock divide-by-zero quotient is all ones. */
        return 1;
    }
    if (quotient == UINT64_C(0x8000000000000000)) {
        return INT64_MIN;
    }
    if (quotient > (uint64_t)INT64_MAX) {
        return -1;
    }
    return (int64_t)quotient;
}

uint64_t open_cfw_em9305_metaware_shift_left64_candidate(
    uint64_t value,
    uint32_t count
)
{
    return open_cfw_em9305_shift_left64_words(value, count);
}

uint64_t open_cfw_em9305_metaware_shift_right64_candidate(
    uint64_t value,
    uint32_t count
)
{
    return open_cfw_em9305_shift_right64_words(value, count);
}

uint32_t open_cfw_em9305_metaware_stack_pointer_in_bounds(
    uintptr_t stack_pointer,
    uintptr_t low_limit,
    uintptr_t high_limit
)
{
    return (uint32_t)(
        low_limit <= high_limit &&
        stack_pointer >= low_limit &&
        stack_pointer <= high_limit
    );
}

uint32_t open_cfw_em9305_metaware_stack_guard_candidate(
    uintptr_t stack_pointer,
    open_cfw_em9305_stack_trap_t trap,
    void *trap_context
)
{
    uint32_t valid = open_cfw_em9305_metaware_stack_pointer_in_bounds(
        stack_pointer,
        OPEN_CFW_EM9305_STACK_LIMIT_LOW,
        OPEN_CFW_EM9305_STACK_LIMIT_HIGH
    );

    if (valid == 0u && trap != 0) {
        trap(trap_context);
    }
    return valid;
}
