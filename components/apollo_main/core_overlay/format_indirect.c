/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 indirect-field callback helper.
 */

typedef unsigned int open_cfw_format_indirect_word;

typedef unsigned int (*open_cfw_format_indirect_callback_fn)(
    void *argument,
    void *output
);

#ifndef OPEN_CFW_FORMAT_INDIRECT_CALLBACK
#define OPEN_CFW_FORMAT_INDIRECT_CALLBACK(field) \
    (*(open_cfw_format_indirect_callback_fn const *)(const void *)( \
        (const unsigned char *)( \
            *(const void * const *)(const void *)(field) \
        ) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_INDIRECT_SET_ERROR
static void open_cfw_format_indirect_set_error(
    void *output,
    open_cfw_format_indirect_word error
)
{
    open_cfw_format_indirect_word *current =
        (open_cfw_format_indirect_word *)(void *)(
            (unsigned char *)output + 0x10U
        );

    if (*current == 0U) {
        *current = error;
    }
}
#define OPEN_CFW_FORMAT_INDIRECT_SET_ERROR(output, error) \
    open_cfw_format_indirect_set_error((output), (error))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_indirect_field_encode(
    void *output,
    const void *field
)
{
    open_cfw_format_indirect_callback_fn callback =
        OPEN_CFW_FORMAT_INDIRECT_CALLBACK(field);

    if (callback == (open_cfw_format_indirect_callback_fn)0) {
        return 1U;
    }
    if (callback((void *)0, output) != 0U) {
        return 1U;
    }

    OPEN_CFW_FORMAT_INDIRECT_SET_ERROR(output, 0x00787CF0U);
    return 0U;
}
