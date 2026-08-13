/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 fixed four- and eight-byte
 * formatting append wrappers at 0x00490D36 and 0x00490D40.
 */

unsigned int open_cfw_format_append(
    void *output,
    const void *data,
    unsigned int length
);

#ifndef OPEN_CFW_FORMAT_FIXED_APPEND
#define OPEN_CFW_FORMAT_FIXED_APPEND(output, data, length) \
    (open_cfw_format_append((output), (data), (length)))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_fixed4_write(
    void *output,
    const void *data
)
{
    return OPEN_CFW_FORMAT_FIXED_APPEND(output, data, 4U);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_fixed8_write(
    void *output,
    const void *data
)
{
    return OPEN_CFW_FORMAT_FIXED_APPEND(output, data, 8U);
}
