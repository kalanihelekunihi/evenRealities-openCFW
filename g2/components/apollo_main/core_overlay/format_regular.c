/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 regular field encoder.
 */

typedef unsigned int open_cfw_format_regular_word;

typedef unsigned int (*open_cfw_format_regular_encode_fn)(
    void *output,
    const void *field
);

unsigned int open_cfw_format_read_bool(const void *value);
unsigned int open_cfw_format_default_check(const void *field);
unsigned int open_cfw_format_repeated_field_encode(
    void *output,
    void *field
);

#ifndef OPEN_CFW_FORMAT_REGULAR_TYPE
#define OPEN_CFW_FORMAT_REGULAR_TYPE(field) \
    ((unsigned int)((const unsigned char *)(field))[0x16])
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_TAG
#define OPEN_CFW_FORMAT_REGULAR_TAG(field) \
    ((unsigned int)((const unsigned char *)(field))[0x10] \
        | ((unsigned int)((const unsigned char *)(field))[0x11] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_DATA
#define OPEN_CFW_FORMAT_REGULAR_DATA(field) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_AUX
#define OPEN_CFW_FORMAT_REGULAR_AUX(field) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x20U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_AUX_TAG
#define OPEN_CFW_FORMAT_REGULAR_AUX_TAG(aux) \
    ((unsigned int)((const unsigned char *)(aux))[0] \
        | ((unsigned int)((const unsigned char *)(aux))[1] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_READ_BOOL
#define OPEN_CFW_FORMAT_REGULAR_READ_BOOL(value) \
    open_cfw_format_read_bool((value))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_DEFAULT_CHECK
#define OPEN_CFW_FORMAT_REGULAR_DEFAULT_CHECK(field) \
    open_cfw_format_default_check((field))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_INDIRECT_ENCODE
#define OPEN_CFW_FORMAT_REGULAR_INDIRECT_ENCODE(output, field) \
    (((open_cfw_format_regular_encode_fn)0x00490AEBU)( \
        (output), \
        (field) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_REPEATED_ENCODE
#define OPEN_CFW_FORMAT_REGULAR_REPEATED_ENCODE(output, field) \
    open_cfw_format_repeated_field_encode((output), (void *)(field))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_VALUE_ENCODE
#define OPEN_CFW_FORMAT_REGULAR_VALUE_ENCODE(output, field) \
    (((open_cfw_format_regular_encode_fn)0x00490A47U)( \
        (output), \
        (field) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REGULAR_SET_ERROR
static void open_cfw_format_regular_set_error(
    void *output,
    open_cfw_format_regular_word error
)
{
    open_cfw_format_regular_word *current =
        (open_cfw_format_regular_word *)(void *)(
            (unsigned char *)output + 0x10U
        );

    if (*current == 0U) {
        *current = error;
    }
}
#define OPEN_CFW_FORMAT_REGULAR_SET_ERROR(output, error) \
    open_cfw_format_regular_set_error((output), (error))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_format_regular_field_encode(
    void *output,
    const void *field
)
{
    unsigned int type = OPEN_CFW_FORMAT_REGULAR_TYPE(field);
    unsigned int allocation = type & 0x30U;
    const void *auxiliary = OPEN_CFW_FORMAT_REGULAR_AUX(field);

    if (allocation == 0x30U) {
        if (
            OPEN_CFW_FORMAT_REGULAR_AUX_TAG(auxiliary)
            != OPEN_CFW_FORMAT_REGULAR_TAG(field)
        ) {
            return 1U;
        }
    } else if (allocation == 0x10U) {
        if (auxiliary != (const void *)0) {
            if (OPEN_CFW_FORMAT_REGULAR_READ_BOOL(auxiliary) == 0U) {
                return 1U;
            }
        } else if (
            ((type & 0xC0U) == 0U)
            && (OPEN_CFW_FORMAT_REGULAR_DEFAULT_CHECK(field) != 0U)
        ) {
            return 1U;
        }
    }

    if (OPEN_CFW_FORMAT_REGULAR_DATA(field) == (const void *)0) {
        if (allocation == 0U) {
            OPEN_CFW_FORMAT_REGULAR_SET_ERROR(output, 0x00779FC4U);
            return 0U;
        }
        return 1U;
    }

    if ((type & 0xC0U) == 0x40U) {
        return OPEN_CFW_FORMAT_REGULAR_INDIRECT_ENCODE(output, field);
    }
    if (allocation == 0x20U) {
        return OPEN_CFW_FORMAT_REGULAR_REPEATED_ENCODE(output, field);
    }
    return OPEN_CFW_FORMAT_REGULAR_VALUE_ENCODE(output, field);
}
