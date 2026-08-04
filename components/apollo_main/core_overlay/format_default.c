/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 protobuf-style default-value
 * checker used by the regular field encoder.
 */

typedef unsigned int (*open_cfw_format_default_iterator_begin_fn)(
    void *iterator,
    const void *message_descriptor,
    const void *source
);

typedef unsigned int (*open_cfw_format_default_iterator_next_fn)(
    void *iterator
);

unsigned int open_cfw_format_read_bool(const void *value);

#ifndef OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BYTES
#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BYTES 40U
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_TYPE
#define OPEN_CFW_FORMAT_DEFAULT_TYPE(field) \
    ((unsigned int)((const unsigned char *)(field))[0x16])
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_LENGTH
#define OPEN_CFW_FORMAT_DEFAULT_LENGTH(field) \
    ((unsigned int)((const unsigned char *)(field))[0x12] \
        | ((unsigned int)((const unsigned char *)(field))[0x13] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_DATA
#define OPEN_CFW_FORMAT_DEFAULT_DATA(field) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_AUX
#define OPEN_CFW_FORMAT_DEFAULT_AUX(field) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x20U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_SUBDESCRIPTOR
#define OPEN_CFW_FORMAT_DEFAULT_SUBDESCRIPTOR(field) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x24U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_METADATA_GUARD
#define OPEN_CFW_FORMAT_DEFAULT_METADATA_GUARD(field) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)( \
            *(const void * const *)(const void *)(field) \
        ) + 0x08U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_METADATA_CALLBACK
#define OPEN_CFW_FORMAT_DEFAULT_METADATA_CALLBACK(field) \
    (*(const unsigned int *)(const void *)( \
        (const unsigned char *)( \
            *(const void * const *)(const void *)(field) \
        ) + 0x0CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_READ_BOOL
#define OPEN_CFW_FORMAT_DEFAULT_READ_BOOL(value) \
    open_cfw_format_read_bool((value))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_READ_U16
#define OPEN_CFW_FORMAT_DEFAULT_READ_U16(value) \
    (*(const unsigned short *)(const void *)(value))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_READ_U32
#define OPEN_CFW_FORMAT_DEFAULT_READ_U32(value) \
    (*(const unsigned int *)(const void *)(value))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BEGIN
#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BEGIN( \
    iterator, \
    descriptor, \
    source \
) \
    (((open_cfw_format_default_iterator_begin_fn)0x004D9385U)( \
        (iterator), \
        (descriptor), \
        (source) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_ITERATOR_NEXT
#define OPEN_CFW_FORMAT_DEFAULT_ITERATOR_NEXT(iterator) \
    (((open_cfw_format_default_iterator_next_fn)0x004D93D9U)(iterator))
#endif

#ifndef OPEN_CFW_FORMAT_DEFAULT_SPECIAL_CALLBACK
#define OPEN_CFW_FORMAT_DEFAULT_SPECIAL_CALLBACK 0x004D94E7U
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_default_check(const void *field)
{
    unsigned int type = OPEN_CFW_FORMAT_DEFAULT_TYPE(field);
    unsigned int storage = type & 0xC0U;
    unsigned int allocation = type & 0x30U;
    unsigned int kind = type & 0x0FU;
    const void *data = OPEN_CFW_FORMAT_DEFAULT_DATA(field);

    if (storage == 0U) {
        const void *auxiliary = OPEN_CFW_FORMAT_DEFAULT_AUX(field);

        if (allocation == 0U) {
            return 0U;
        }
        if ((allocation == 0x20U) || (allocation == 0x30U)) {
            return OPEN_CFW_FORMAT_DEFAULT_READ_U16(auxiliary) == 0U;
        }
        if (auxiliary != (const void *)0) {
            return OPEN_CFW_FORMAT_DEFAULT_READ_BOOL(auxiliary) == 0U;
        }
        if (OPEN_CFW_FORMAT_DEFAULT_METADATA_GUARD(field) != 0U) {
            return 0U;
        }
        if (kind < 6U) {
            const unsigned char *bytes =
                (const unsigned char *)data;
            unsigned int index;
            unsigned int length = OPEN_CFW_FORMAT_DEFAULT_LENGTH(field);

            for (index = 0U; index < length; index += 1U) {
                if (bytes[index] != 0U) {
                    return 0U;
                }
            }
            return 1U;
        }
        if (kind == 6U) {
            return OPEN_CFW_FORMAT_DEFAULT_READ_U16(data) == 0U;
        }
        if (kind == 7U) {
            return *(const unsigned char *)data == 0U;
        }
        if (kind == 11U) {
            return OPEN_CFW_FORMAT_DEFAULT_LENGTH(field) == 0U;
        }
        if ((kind == 8U) || (kind == 9U)) {
            unsigned char iterator[
                OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BYTES
            ];

            if (
                OPEN_CFW_FORMAT_DEFAULT_ITERATOR_BEGIN(
                    iterator,
                    OPEN_CFW_FORMAT_DEFAULT_SUBDESCRIPTOR(field),
                    data
                ) == 0U
            ) {
                return 1U;
            }
            do {
                if (open_cfw_format_default_check(iterator) == 0U) {
                    return 0U;
                }
            } while (
                OPEN_CFW_FORMAT_DEFAULT_ITERATOR_NEXT(iterator) != 0U
            );
            return 1U;
        }
        return 0U;
    }

    if (storage == 0x80U) {
        return data == (const void *)0;
    }
    if (storage == 0x40U) {
        unsigned int callback;

        if (kind == 10U) {
            return OPEN_CFW_FORMAT_DEFAULT_READ_U32(data) == 0U;
        }
        callback = OPEN_CFW_FORMAT_DEFAULT_METADATA_CALLBACK(field);
        if (callback == OPEN_CFW_FORMAT_DEFAULT_SPECIAL_CALLBACK) {
            return OPEN_CFW_FORMAT_DEFAULT_READ_U32(data) == 0U;
        }
        return callback == 0U;
    }
    return 0U;
}
