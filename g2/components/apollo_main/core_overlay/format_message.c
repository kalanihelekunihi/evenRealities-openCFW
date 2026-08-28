/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 generic message encoder.
 */

typedef unsigned int (*open_cfw_format_message_iterator_begin_fn)(
    void *iterator,
    const void *message_descriptor,
    const void *source
);

typedef unsigned int (*open_cfw_format_message_iterator_next_fn)(
    void *iterator
);

typedef unsigned int (*open_cfw_format_message_field_encode_fn)(
    void *output,
    const void *iterator
);

#ifndef OPEN_CFW_FORMAT_MESSAGE_ITERATOR_BEGIN
#define OPEN_CFW_FORMAT_MESSAGE_ITERATOR_BEGIN( \
    iterator, \
    descriptor, \
    source \
) \
    (((open_cfw_format_message_iterator_begin_fn)0x004D94BBU)( \
        (iterator), \
        (descriptor), \
        (source) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_MESSAGE_ITERATOR_NEXT
#define OPEN_CFW_FORMAT_MESSAGE_ITERATOR_NEXT(iterator) \
    (((open_cfw_format_message_iterator_next_fn)0x004D93D9U)(iterator))
#endif

#ifndef OPEN_CFW_FORMAT_MESSAGE_FIELD_ENCODE
#define OPEN_CFW_FORMAT_MESSAGE_FIELD_ENCODE(output, iterator) \
    (((open_cfw_format_message_field_encode_fn)0x00490B1FU)( \
        (output), \
        (iterator) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_MESSAGE_EXTENSION_ENCODE
#define OPEN_CFW_FORMAT_MESSAGE_EXTENSION_ENCODE(output, iterator) \
    (((open_cfw_format_message_field_encode_fn)0x00490BF9U)( \
        (output), \
        (iterator) \
    ))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_message_encode(
    void *output,
    const void *message_descriptor,
    const void *source
)
{
    unsigned char iterator[40];

    if (
        OPEN_CFW_FORMAT_MESSAGE_ITERATOR_BEGIN(
            iterator,
            message_descriptor,
            source
        ) == 0U
    ) {
        return 1U;
    }

    do {
        unsigned int status;

        if ((iterator[0x16] & 0x0FU) == 10U) {
            status = OPEN_CFW_FORMAT_MESSAGE_EXTENSION_ENCODE(
                output,
                iterator
            );
        } else {
            status = OPEN_CFW_FORMAT_MESSAGE_FIELD_ENCODE(
                output,
                iterator
            );
        }
        if (status == 0U) {
            return 0U;
        }
    } while (OPEN_CFW_FORMAT_MESSAGE_ITERATOR_NEXT(iterator) != 0U);

    return 1U;
}
