/*
 * Focused 32-bit models of the official LZ4 v1.10.0 and v1.9.4
 * read_variable_length source forms.  This fixture exists because the native
 * Apple/Linux host ABI uses 64-bit size_t while the G2 target uses 32-bit
 * size_t.  It is test-only and is not a firmware build input.
 */

#include <stddef.h>
#include <stdint.h>

static int finish(
    uint32_t length,
    size_t position,
    uint32_t *length_out,
    size_t *position_out
)
{
    *length_out = length;
    *position_out = position;
    return 0;
}

static int fail(
    uint32_t length,
    size_t position,
    uint32_t *length_out,
    size_t *position_out
)
{
    *length_out = length;
    *position_out = position;
    return -1;
}

int open_cfw_lz4_rvl_v1_10_0_u32(
    const uint8_t *input,
    size_t input_size,
    size_t limit,
    int initial_check,
    uint32_t *length_out,
    size_t *position_out
)
{
    size_t position = 0U;
    uint32_t s;
    uint32_t length = 0U;

    if (
        input == NULL ||
        length_out == NULL ||
        position_out == NULL ||
        limit > input_size
    ) {
        return -2;
    }
    if (initial_check != 0 && position >= limit) {
        return fail(length, position, length_out, position_out);
    }
    if (position >= input_size) {
        return fail(length, position, length_out, position_out);
    }
    s = input[position++];
    length += s;
    if (position > limit || length > UINT32_C(0x7fffffff)) {
        return fail(length, position, length_out, position_out);
    }
    if (s != UINT32_C(255)) {
        return finish(length, position, length_out, position_out);
    }
    do {
        if (position >= input_size) {
            return fail(length, position, length_out, position_out);
        }
        s = input[position++];
        length += s;
        if (position > limit || length > UINT32_C(0x7fffffff)) {
            return fail(length, position, length_out, position_out);
        }
    } while (s == UINT32_C(255));
    return finish(length, position, length_out, position_out);
}

int open_cfw_lz4_rvl_v1_9_4_u32(
    const uint8_t *input,
    size_t input_size,
    size_t limit,
    int initial_check,
    uint32_t *length_out,
    size_t *position_out
)
{
    size_t position = 0U;
    uint32_t s;
    uint32_t length = 0U;

    if (
        input == NULL ||
        length_out == NULL ||
        position_out == NULL ||
        limit > input_size
    ) {
        return -2;
    }
    if (initial_check != 0 && position >= limit) {
        return fail(length, position, length_out, position_out);
    }
    do {
        if (position >= input_size) {
            return fail(length, position, length_out, position_out);
        }
        s = input[position++];
        length += s;
        if (position > limit || length > UINT32_C(0x7fffffff)) {
            return fail(length, position, length_out, position_out);
        }
    } while (s == UINT32_C(255));
    return finish(length, position, length_out, position_out);
}
