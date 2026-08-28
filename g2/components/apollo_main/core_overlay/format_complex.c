/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 formatting submessage writer and
 * bytes, string, and submessage-field descriptor adapters.
 */

typedef unsigned int open_cfw_format_complex_word;

typedef unsigned int (*open_cfw_format_message_encode_fn)(
    void *output,
    const void *message_descriptor,
    const void *source
);

typedef unsigned int (*open_cfw_format_extension_encode_fn)(
    void *output,
    const void *field_descriptor,
    const void *argument
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
unsigned int open_cfw_format_buffer_write(
    void *output,
    const void *data,
    unsigned int length
);

#ifndef OPEN_CFW_FORMAT_COMPLEX_MESSAGE_ENCODE
#define OPEN_CFW_FORMAT_COMPLEX_MESSAGE_ENCODE(output, descriptor, source) \
    (((open_cfw_format_message_encode_fn)0x00490C33U)( \
        (output), \
        (descriptor), \
        (source) \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_PREFIX
#define OPEN_CFW_FORMAT_COMPLEX_PREFIX(output, length) \
    open_cfw_format_u64_prefix_write( \
        (output), \
        (unsigned long long)(length) \
    )
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_APPEND
#define OPEN_CFW_FORMAT_COMPLEX_APPEND(output, data, length) \
    open_cfw_format_append((output), (data), (length))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_BUFFER
#define OPEN_CFW_FORMAT_COMPLEX_BUFFER(output, data, length) \
    open_cfw_format_buffer_write((output), (data), (length))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_DATA
#define OPEN_CFW_FORMAT_COMPLEX_DATA(descriptor) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x1CU \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_EXTENSION
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION(descriptor) \
    (*(const unsigned char * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x20U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_SUBMESSAGE
#define OPEN_CFW_FORMAT_COMPLEX_SUBMESSAGE(descriptor) \
    (*(const void * const *)(const void *)( \
        (const unsigned char *)(descriptor) + 0x24U \
    ))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALLBACK
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALLBACK(record) \
    (*(open_cfw_format_extension_encode_fn const *)(const void *)(record))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALL
#define OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALL( \
    callback, \
    output, \
    descriptor, \
    argument \
) \
    ((callback)((output), (descriptor), (argument)))
#endif

#ifndef OPEN_CFW_FORMAT_COMPLEX_SET_ERROR
static void open_cfw_format_complex_set_error(
    void *output,
    open_cfw_format_complex_word error
)
{
    open_cfw_format_complex_word *current =
        (open_cfw_format_complex_word *)(void *)(
            (unsigned char *)output + 0x10U
        );

    if (*current == 0U) {
        *current = error;
    }
}
#define OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, error) \
    open_cfw_format_complex_set_error((output), (error))
#endif

static open_cfw_format_complex_word open_cfw_format_complex_read_word(
    const void *object,
    unsigned int offset
)
{
    return *(const open_cfw_format_complex_word *)(const void *)(
        (const unsigned char *)object + offset
    );
}

static void open_cfw_format_complex_write_word(
    void *object,
    unsigned int offset,
    open_cfw_format_complex_word value
)
{
    *(open_cfw_format_complex_word *)(void *)(
        (unsigned char *)object + offset
    ) = value;
}

static unsigned int open_cfw_format_complex_read_half(
    const void *object,
    unsigned int offset
)
{
    const unsigned char *value =
        (const unsigned char *)object + offset;

    return (unsigned int)value[0]
        | ((unsigned int)value[1] << 8U);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_submessage_write(
    void *output,
    const void *message_descriptor,
    const void *source
)
{
    open_cfw_format_complex_word sizing[5] = {0U, 0U, 0U, 0U, 0U};
    open_cfw_format_complex_word length;
    unsigned int status;

    if (
        OPEN_CFW_FORMAT_COMPLEX_MESSAGE_ENCODE(
            sizing,
            message_descriptor,
            source
        ) == 0U
    ) {
        open_cfw_format_complex_write_word(
            output,
            0x10U,
            sizing[4]
        );
        return 0U;
    }

    length = sizing[3];
    if (OPEN_CFW_FORMAT_COMPLEX_PREFIX(output, length) == 0U) {
        return 0U;
    }

    if (open_cfw_format_complex_read_word(output, 0x00U) == 0U) {
        return OPEN_CFW_FORMAT_COMPLEX_APPEND(
            output,
            (const void *)0,
            length
        );
    }

    if (
        open_cfw_format_complex_read_word(output, 0x08U)
        < (
            open_cfw_format_complex_read_word(output, 0x0CU)
            + length
        )
    ) {
        OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x0078B6A8U);
        return 0U;
    }

    sizing[0] = open_cfw_format_complex_read_word(output, 0x00U);
    sizing[1] = open_cfw_format_complex_read_word(output, 0x04U);
    sizing[2] = length;
    sizing[3] = 0U;
    sizing[4] = 0U;
    status = OPEN_CFW_FORMAT_COMPLEX_MESSAGE_ENCODE(
        sizing,
        message_descriptor,
        source
    );

    open_cfw_format_complex_write_word(
        output,
        0x0CU,
        open_cfw_format_complex_read_word(output, 0x0CU) + sizing[3]
    );
    open_cfw_format_complex_write_word(output, 0x04U, sizing[1]);
    open_cfw_format_complex_write_word(output, 0x10U, sizing[4]);

    if (sizing[3] != length) {
        OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x0078187CU);
        return 0U;
    }
    return status & 0xFFU;
}

__attribute__((used, noinline))
unsigned int open_cfw_format_bytes_write(
    void *output,
    const void *descriptor
)
{
    const unsigned char *bytes =
        (const unsigned char *)OPEN_CFW_FORMAT_COMPLEX_DATA(descriptor);
    unsigned int length;

    if (bytes == (const unsigned char *)0) {
        return OPEN_CFW_FORMAT_COMPLEX_BUFFER(
            output,
            (const void *)0,
            0U
        );
    }

    length = (unsigned int)bytes[0]
        | ((unsigned int)bytes[1] << 8U);
    if (
        ((((const unsigned char *)descriptor)[0x16] & 0xC0U) == 0U)
        && (
            (
                open_cfw_format_complex_read_half(
                    descriptor,
                    0x12U
                ) - 2U
            ) < length
        )
    ) {
        OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x007818A4U);
        return 0U;
    }

    return OPEN_CFW_FORMAT_COMPLEX_BUFFER(output, bytes + 2U, length);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_string_write(
    void *output,
    const void *descriptor
)
{
    const unsigned char *text =
        (const unsigned char *)OPEN_CFW_FORMAT_COMPLEX_DATA(descriptor);
    const unsigned char *cursor = text;
    unsigned int length = 0U;
    unsigned int maximum;

    if ((((const unsigned char *)descriptor)[0x16] & 0xC0U) == 0x80U) {
        maximum = 0xFFFFFFFFU;
    } else {
        maximum = open_cfw_format_complex_read_half(descriptor, 0x12U);
        if (maximum == 0U) {
            OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x007818B8U);
            return 0U;
        }
        maximum -= 1U;
    }

    if (text == (const unsigned char *)0) {
        return OPEN_CFW_FORMAT_COMPLEX_BUFFER(
            output,
            (const void *)0,
            0U
        );
    }

    while ((length < maximum) && (*cursor != 0U)) {
        length += 1U;
        cursor += 1U;
    }
    if (*cursor != 0U) {
        OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x007818CCU);
        return 0U;
    }
    return OPEN_CFW_FORMAT_COMPLEX_BUFFER(output, text, length);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_submessage_field_write(
    void *output,
    const void *descriptor
)
{
    const void *submessage =
        OPEN_CFW_FORMAT_COMPLEX_SUBMESSAGE(descriptor);
    const unsigned char *extension;

    if (submessage == (const void *)0) {
        OPEN_CFW_FORMAT_COMPLEX_SET_ERROR(output, 0x0076F470U);
        return 0U;
    }

    extension = OPEN_CFW_FORMAT_COMPLEX_EXTENSION(descriptor);
    if (
        ((((const unsigned char *)descriptor)[0x16] & 0x0FU) == 9U)
        && (extension != (const unsigned char *)0)
    ) {
        const unsigned char *record = extension - 8U;
        open_cfw_format_extension_encode_fn callback =
            OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALLBACK(record);

        if (
            (callback != (open_cfw_format_extension_encode_fn)0)
            && (
                OPEN_CFW_FORMAT_COMPLEX_EXTENSION_CALL(
                    callback,
                    output,
                    descriptor,
                    record + 4U
                ) == 0U
            )
        ) {
            return 0U;
        }
    }

    return open_cfw_format_submessage_write(
        output,
        submessage,
        OPEN_CFW_FORMAT_COMPLEX_DATA(descriptor)
    );
}
