/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 field-value dispatcher.
 */

typedef unsigned int open_cfw_format_value_word;

unsigned int open_cfw_format_descriptor_key_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_bool_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_integer_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_fixed_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_bytes_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_string_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_submessage_field_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_span(
    void *output,
    const void *descriptor
);

#ifndef OPEN_CFW_FORMAT_VALUE_TYPE
#define OPEN_CFW_FORMAT_VALUE_TYPE(descriptor) \
    ((unsigned int)((const unsigned char *)(descriptor))[0x16])
#endif

#ifndef OPEN_CFW_FORMAT_VALUE_DATA
#define OPEN_CFW_FORMAT_VALUE_DATA(descriptor) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_VALUE_SET_ERROR
static void open_cfw_format_value_set_error(
    void *output,
    open_cfw_format_value_word error
)
{
    open_cfw_format_value_word *current =
        (open_cfw_format_value_word *)(void *)(
            (unsigned char *)output + 0x10U
        );

    if (*current == 0U) {
        *current = error;
    }
}
#define OPEN_CFW_FORMAT_VALUE_SET_ERROR(output, error) \
    open_cfw_format_value_set_error((output), (error))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_value_encode(
    void *output,
    const void *descriptor
)
{
    unsigned int type;

    if (OPEN_CFW_FORMAT_VALUE_DATA(descriptor) == (const void *)0) {
        return 1U;
    }
    if (open_cfw_format_descriptor_key_write(output, descriptor) == 0U) {
        return 0U;
    }

    type = OPEN_CFW_FORMAT_VALUE_TYPE(descriptor) & 0x0FU;
    if (type == 0U) {
        return open_cfw_format_bool_write(output, descriptor);
    }
    if ((type >= 1U) && (type <= 3U)) {
        return open_cfw_format_integer_write(output, descriptor);
    }
    if ((type == 4U) || (type == 5U)) {
        return open_cfw_format_fixed_write(output, descriptor);
    }
    if (type == 6U) {
        return open_cfw_format_bytes_write(output, descriptor);
    }
    if (type == 7U) {
        return open_cfw_format_string_write(output, descriptor);
    }
    if ((type == 8U) || (type == 9U)) {
        return open_cfw_format_submessage_field_write(output, descriptor);
    }
    if (type == 11U) {
        return open_cfw_format_span(output, descriptor);
    }

    OPEN_CFW_FORMAT_VALUE_SET_ERROR(output, 0x00781854U);
    return 0U;
}
