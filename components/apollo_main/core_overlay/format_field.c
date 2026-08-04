/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacements for the G2 2.2.6.10 formatting field-key encoder at
 * 0x00490D4A and descriptor adapter at 0x00490D66.
 */

unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
);

#ifndef OPEN_CFW_FORMAT_FIELD_PREFIX
#define OPEN_CFW_FORMAT_FIELD_PREFIX(output, value) \
    (open_cfw_format_u64_prefix_write((output), (value)))
#endif

#ifndef OPEN_CFW_FORMAT_FIELD_SET_INVALID
static void open_cfw_format_field_set_invalid(void *output)
{
    const char **error = (const char **)((unsigned char *)output + 0x10U);

    if (*error == (const char *)0) {
        *error = (const char *)0x00781854U;
    }
}
#define OPEN_CFW_FORMAT_FIELD_SET_INVALID(output) \
    open_cfw_format_field_set_invalid((output))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_field_key_write(
    void *output,
    unsigned int wire_type,
    unsigned int field_number
)
{
    const unsigned long long key =
        ((unsigned long long)field_number << 3U)
        | (unsigned long long)(wire_type & 0xFFU);

    return OPEN_CFW_FORMAT_FIELD_PREFIX(output, key);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_descriptor_key_write(
    void *output,
    const void *descriptor
)
{
    const unsigned char *bytes = (const unsigned char *)descriptor;
    const unsigned int format_type = (unsigned int)(bytes[0x16] & 0x0FU);
    const unsigned int field_number =
        (unsigned int)bytes[0x10]
        | ((unsigned int)bytes[0x11] << 8U);
    unsigned int wire_type;

    if (format_type <= 3U) {
        wire_type = 0U;
    } else if (format_type == 4U) {
        wire_type = 5U;
    } else if (format_type == 5U) {
        wire_type = 1U;
    } else if (
        ((format_type >= 6U) && (format_type <= 9U))
        || (format_type == 11U)
    ) {
        wire_type = 2U;
    } else {
        OPEN_CFW_FORMAT_FIELD_SET_INVALID(output);
        return 0U;
    }

    return open_cfw_format_field_key_write(
        output,
        wire_type,
        field_number
    );
}
