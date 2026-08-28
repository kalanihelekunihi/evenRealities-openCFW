/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 repeated-field encoder.
 */

struct open_cfw_format_repeated_output {
    void *write;
    void *context;
    unsigned int capacity;
    unsigned int length;
    const char *error;
};

unsigned int open_cfw_format_field_key_write(
    void *output,
    unsigned int wire_type,
    unsigned int field_number
);
unsigned int open_cfw_format_descriptor_key_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
);
unsigned int open_cfw_format_append(
    void *output,
    const void *data,
    unsigned int length
);
unsigned int open_cfw_format_integer_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_fixed_write(
    void *output,
    const void *descriptor
);
unsigned int open_cfw_format_value_encode(
    void *output,
    const void *descriptor
);

#ifndef OPEN_CFW_FORMAT_REPEATED_TYPE
#define OPEN_CFW_FORMAT_REPEATED_TYPE(field) \
    ((unsigned int)((const unsigned char *)(field))[0x16])
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_TAG
#define OPEN_CFW_FORMAT_REPEATED_TAG(field) \
    ((unsigned int)((const unsigned char *)(field))[0x10] \
        | ((unsigned int)((const unsigned char *)(field))[0x11] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_ELEMENT_SIZE
#define OPEN_CFW_FORMAT_REPEATED_ELEMENT_SIZE(field) \
    ((unsigned int)((const unsigned char *)(field))[0x12] \
        | ((unsigned int)((const unsigned char *)(field))[0x13] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_MAX_COUNT
#define OPEN_CFW_FORMAT_REPEATED_MAX_COUNT(field) \
    ((unsigned int)((const unsigned char *)(field))[0x14] \
        | ((unsigned int)((const unsigned char *)(field))[0x15] << 8U))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_DATA
#define OPEN_CFW_FORMAT_REPEATED_DATA(field) \
    (*(void * const *)(const void *)( \
        (const unsigned char *)(field) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_SET_DATA
#define OPEN_CFW_FORMAT_REPEATED_SET_DATA(field, value) \
    (*(void **)(void *)( \
        (unsigned char *)(field) + 0x1CU \
    ) = (void *)(value))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_COUNT
#define OPEN_CFW_FORMAT_REPEATED_COUNT(field) \
    (*(const unsigned short *)(const void *)( \
        *(const void * const *)(const void *)( \
            (const unsigned char *)(field) + 0x20U \
        ) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_OUTPUT_WRITER
#define OPEN_CFW_FORMAT_REPEATED_OUTPUT_WRITER(output) \
    (((struct open_cfw_format_repeated_output *)(output))->write)
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_OUTPUT_ERROR
#define OPEN_CFW_FORMAT_REPEATED_OUTPUT_ERROR(output) \
    (((struct open_cfw_format_repeated_output *)(output))->error)
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_SET_OUTPUT_ERROR
#define OPEN_CFW_FORMAT_REPEATED_SET_OUTPUT_ERROR(output, value) \
    (((struct open_cfw_format_repeated_output *)(output))->error = (value))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_FIELD_KEY
#define OPEN_CFW_FORMAT_REPEATED_FIELD_KEY(output, wire_type, tag) \
    open_cfw_format_field_key_write((output), (wire_type), (tag))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_DESCRIPTOR_KEY
#define OPEN_CFW_FORMAT_REPEATED_DESCRIPTOR_KEY(output, field) \
    open_cfw_format_descriptor_key_write((output), (field))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_PREFIX
#define OPEN_CFW_FORMAT_REPEATED_PREFIX(output, value) \
    open_cfw_format_u64_prefix_write((output), (value))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_APPEND
#define OPEN_CFW_FORMAT_REPEATED_APPEND(output, data, length) \
    open_cfw_format_append((output), (data), (length))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_INTEGER
#define OPEN_CFW_FORMAT_REPEATED_INTEGER(output, field) \
    open_cfw_format_integer_write((output), (field))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_FIXED
#define OPEN_CFW_FORMAT_REPEATED_FIXED(output, field) \
    open_cfw_format_fixed_write((output), (field))
#endif

#ifndef OPEN_CFW_FORMAT_REPEATED_VALUE
#define OPEN_CFW_FORMAT_REPEATED_VALUE(output, field) \
    open_cfw_format_value_encode((output), (field))
#endif

static void open_cfw_format_repeated_install_error(
    void *output,
    const char *error
)
{
    if (OPEN_CFW_FORMAT_REPEATED_OUTPUT_ERROR(output) == (const char *)0) {
        OPEN_CFW_FORMAT_REPEATED_SET_OUTPUT_ERROR(output, error);
    }
}

static void open_cfw_format_repeated_advance(void *field)
{
    OPEN_CFW_FORMAT_REPEATED_SET_DATA(
        field,
        (unsigned char *)OPEN_CFW_FORMAT_REPEATED_DATA(field)
            + OPEN_CFW_FORMAT_REPEATED_ELEMENT_SIZE(field)
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_format_repeated_field_encode(
    void *output,
    void *field
)
{
    const unsigned int count = OPEN_CFW_FORMAT_REPEATED_COUNT(field);
    const unsigned int type = OPEN_CFW_FORMAT_REPEATED_TYPE(field);
    const unsigned int storage = type & 0xC0U;
    const unsigned int kind = type & 0x0FU;
    unsigned int index;

    if (count == 0U) {
        return 1U;
    }
    if (
        (storage != 0x80U)
        && (OPEN_CFW_FORMAT_REPEATED_MAX_COUNT(field) < count)
    ) {
        open_cfw_format_repeated_install_error(
            output,
            (const char *)0x00779FACU
        );
        return 0U;
    }

    if (kind < 6U) {
        unsigned int packed_size;

        if (
            OPEN_CFW_FORMAT_REPEATED_FIELD_KEY(
                output,
                2U,
                OPEN_CFW_FORMAT_REPEATED_TAG(field)
            ) == 0U
        ) {
            return 0U;
        }
        if (kind == 4U) {
            packed_size = count << 2U;
        } else if (kind == 5U) {
            packed_size = count << 3U;
        } else {
            struct open_cfw_format_repeated_output sizing = {
                (void *)0,
                (void *)0,
                0U,
                0U,
                (const char *)0
            };
            void *const original_data =
                OPEN_CFW_FORMAT_REPEATED_DATA(field);

            for (index = 0U; index < count; index += 1U) {
                if (
                    OPEN_CFW_FORMAT_REPEATED_INTEGER(
                        &sizing,
                        field
                    ) == 0U
                ) {
                    const char *error =
                        OPEN_CFW_FORMAT_REPEATED_OUTPUT_ERROR(&sizing);

                    if (error == (const char *)0) {
                        error = (const char *)0x0078DE7CU;
                    }
                    open_cfw_format_repeated_install_error(output, error);
                    return 0U;
                }
                open_cfw_format_repeated_advance(field);
            }
            OPEN_CFW_FORMAT_REPEATED_SET_DATA(field, original_data);
            packed_size = sizing.length;
        }
        if (
            OPEN_CFW_FORMAT_REPEATED_PREFIX(output, packed_size)
            == 0U
        ) {
            return 0U;
        }
        if (
            OPEN_CFW_FORMAT_REPEATED_OUTPUT_WRITER(output)
            == (void *)0
        ) {
            return OPEN_CFW_FORMAT_REPEATED_APPEND(
                output,
                (const void *)0,
                packed_size
            );
        }
        for (index = 0U; index < count; index += 1U) {
            unsigned int status =
                ((kind == 4U) || (kind == 5U))
                    ? OPEN_CFW_FORMAT_REPEATED_FIXED(output, field)
                    : OPEN_CFW_FORMAT_REPEATED_INTEGER(output, field);

            if (status == 0U) {
                return 0U;
            }
            open_cfw_format_repeated_advance(field);
        }
        return 1U;
    }

    for (index = 0U; index < count; index += 1U) {
        unsigned int status;

        if (
            (storage == 0x80U)
            && ((kind == 6U) || (kind == 7U))
        ) {
            void *const original_data =
                OPEN_CFW_FORMAT_REPEATED_DATA(field);

            OPEN_CFW_FORMAT_REPEATED_SET_DATA(
                field,
                *(void * const *)(const void *)original_data
            );
            if (
                OPEN_CFW_FORMAT_REPEATED_DATA(field)
                == (void *)0
            ) {
                status =
                    (
                        OPEN_CFW_FORMAT_REPEATED_DESCRIPTOR_KEY(
                            output,
                            field
                        ) != 0U
                    )
                    && (
                        OPEN_CFW_FORMAT_REPEATED_PREFIX(output, 0U)
                        != 0U
                    );
            } else {
                status = OPEN_CFW_FORMAT_REPEATED_VALUE(output, field);
            }
            OPEN_CFW_FORMAT_REPEATED_SET_DATA(field, original_data);
            if ((status & 0xFFU) == 0U) {
                return 0U;
            }
        } else if (
            OPEN_CFW_FORMAT_REPEATED_VALUE(output, field) == 0U
        ) {
            return 0U;
        }
        open_cfw_format_repeated_advance(field);
    }
    return 1U;
}
