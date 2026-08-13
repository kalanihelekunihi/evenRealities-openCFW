/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 unsigned LEB128 encoder at
 * 0x00490C84 and the unsigned 64-bit prefix writer at 0x00490CE0. Their exact
 * boundaries, callers, and retained append ABI are recorded in EVIDENCE.md.
 */

unsigned int open_cfw_format_append(
    void *output,
    const void *data,
    unsigned int length
);

#ifndef OPEN_CFW_FORMAT_VARINT_APPEND
#define OPEN_CFW_FORMAT_VARINT_APPEND(output, data, length) \
    (open_cfw_format_append( \
        (output), \
        (data), \
        (length) \
    ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_uleb128_write(
    void *output,
    unsigned int low,
    unsigned int high
)
{
    unsigned char encoded[10];
    unsigned int length = 0U;

    while ((high != 0U) || (low >= 0x80U)) {
        encoded[length] = (unsigned char)((low & 0x7FU) | 0x80U);
        length += 1U;
        low = (low >> 7U) | (high << 25U);
        high >>= 7U;
    }
    encoded[length] = (unsigned char)low;
    length += 1U;

    return OPEN_CFW_FORMAT_VARINT_APPEND(output, encoded, length);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
)
{
    if (value < 0x80ULL) {
        const unsigned char encoded = (unsigned char)value;
        return OPEN_CFW_FORMAT_VARINT_APPEND(output, &encoded, 1U);
    }
    return open_cfw_format_uleb128_write(
        output,
        (unsigned int)value,
        (unsigned int)(value >> 32U)
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_format_s64_zigzag_write(
    void *output,
    long long value
)
{
    const unsigned long long bits = (unsigned long long)value;
    const unsigned long long sign_mask = 0ULL - (bits >> 63U);
    const unsigned long long encoded = (bits << 1U) ^ sign_mask;

    return open_cfw_format_u64_prefix_write(output, encoded);
}
