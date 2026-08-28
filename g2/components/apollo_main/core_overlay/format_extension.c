/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 extension-field wrapper and
 * linked extension dispatcher.
 */

typedef unsigned int open_cfw_format_extension_word;

typedef unsigned int (*open_cfw_format_extension_iterator_init_fn)(
    void *iterator,
    const void *field
);

typedef unsigned int (*open_cfw_format_extension_callback_fn)(
    void *output,
    const void *record
);

unsigned int open_cfw_format_regular_field_encode(
    void *output,
    const void *field
);

#ifndef OPEN_CFW_FORMAT_EXTENSION_ITERATOR_INIT
#define OPEN_CFW_FORMAT_EXTENSION_ITERATOR_INIT(iterator, field) \
    (((open_cfw_format_extension_iterator_init_fn)0x004D94D3U)( \
        (iterator), \
        (field) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_EXTENSION_HEAD
#define OPEN_CFW_FORMAT_EXTENSION_HEAD(field) \
    (*(const void * const *)(const void *)( \
        *(const void * const *)(const void *)( \
            (const unsigned char *)(field) + 0x1CU \
        ) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_EXTENSION_NEXT
#define OPEN_CFW_FORMAT_EXTENSION_NEXT(record) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(record) + 0x08U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_EXTENSION_CALLBACK
#define OPEN_CFW_FORMAT_EXTENSION_CALLBACK(record) \
    (*(open_cfw_format_extension_callback_fn const *)(const void *)( \
        (const unsigned char *)( \
            *(const void * const *)(const void *)(record) \
        ) + 0x04U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_EXTENSION_SET_ERROR
static void open_cfw_format_extension_set_error(
    void *output,
    open_cfw_format_extension_word error
)
{
    open_cfw_format_extension_word *current =
        (open_cfw_format_extension_word *)(void *)(
            (unsigned char *)output + 0x10U
        );

    if (*current == 0U) {
        *current = error;
    }
}
#define OPEN_CFW_FORMAT_EXTENSION_SET_ERROR(output, error) \
    open_cfw_format_extension_set_error((output), (error))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_extension_default_encode(
    void *output,
    const void *field
)
{
    unsigned char iterator[40];

    if (
        OPEN_CFW_FORMAT_EXTENSION_ITERATOR_INIT(iterator, field)
        == 0U
    ) {
        OPEN_CFW_FORMAT_EXTENSION_SET_ERROR(output, 0x00781868U);
        return 0U;
    }
    return open_cfw_format_regular_field_encode(output, iterator);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_extension_fields_encode(
    void *output,
    const void *field
)
{
    const void *record = OPEN_CFW_FORMAT_EXTENSION_HEAD(field);

    while (record != (const void *)0) {
        open_cfw_format_extension_callback_fn callback =
            OPEN_CFW_FORMAT_EXTENSION_CALLBACK(record);
        unsigned int status;

        if (callback == (open_cfw_format_extension_callback_fn)0) {
            status = open_cfw_format_extension_default_encode(
                output,
                record
            );
        } else {
            status = callback(output, record);
        }
        if ((status & 0xFFU) == 0U) {
            return 0U;
        }
        record = OPEN_CFW_FORMAT_EXTENSION_NEXT(record);
    }
    return 1U;
}
