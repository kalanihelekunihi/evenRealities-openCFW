/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacements for the G2 2.2.6.10 formatting boolean reader and
 * boolean, integer, and fixed-width descriptor adapters.
 */

unsigned int open_cfw_format_u64_prefix_write(
    void *output,
    unsigned long long value
);
unsigned int open_cfw_format_s64_zigzag_write(
    void *output,
    long long value
);
unsigned int open_cfw_format_fixed4_write(
    void *output,
    const void *data
);
unsigned int open_cfw_format_fixed8_write(
    void *output,
    const void *data
);

#ifndef OPEN_CFW_FORMAT_SCALAR_PREFIX
#define OPEN_CFW_FORMAT_SCALAR_PREFIX(output, value) \
    open_cfw_format_u64_prefix_write((output), (value))
#endif

#ifndef OPEN_CFW_FORMAT_SCALAR_ZIGZAG
#define OPEN_CFW_FORMAT_SCALAR_ZIGZAG(output, value) \
    open_cfw_format_s64_zigzag_write((output), (value))
#endif

#ifndef OPEN_CFW_FORMAT_SCALAR_FIXED4
#define OPEN_CFW_FORMAT_SCALAR_FIXED4(output, data) \
    open_cfw_format_fixed4_write((output), (data))
#endif

#ifndef OPEN_CFW_FORMAT_SCALAR_FIXED8
#define OPEN_CFW_FORMAT_SCALAR_FIXED8(output, data) \
    open_cfw_format_fixed8_write((output), (data))
#endif

#ifndef OPEN_CFW_FORMAT_SCALAR_SET_INVALID_SIZE
static void open_cfw_format_scalar_set_invalid_size(void *output)
{
    const char **error = (const char **)((unsigned char *)output + 0x10U);

    if (*error == (const char *)0) {
        *error = (const char *)0x00781890U;
    }
}
#define OPEN_CFW_FORMAT_SCALAR_SET_INVALID_SIZE(output) \
    open_cfw_format_scalar_set_invalid_size((output))
#endif

static unsigned int open_cfw_format_scalar_size(const unsigned char *descriptor)
{
    return (unsigned int)descriptor[0x12]
        | ((unsigned int)descriptor[0x13] << 8U);
}

static const unsigned char *open_cfw_format_scalar_data(
    const unsigned char *descriptor
)
{
    const unsigned char *const *data =
        (const unsigned char *const *)(descriptor + 0x1CU);
    return *data;
}

static unsigned long long open_cfw_format_scalar_read_unsigned(
    const unsigned char *data,
    unsigned int length
)
{
    if (length == 1U) {
        return (unsigned long long)data[0];
    }
    if (length == 2U) {
        return (unsigned long long)data[0]
            | ((unsigned long long)data[1] << 8U);
    }
    if (length == 4U) {
        return (unsigned long long)data[0]
            | ((unsigned long long)data[1] << 8U)
            | ((unsigned long long)data[2] << 16U)
            | ((unsigned long long)data[3] << 24U);
    }
    return (unsigned long long)data[0]
        | ((unsigned long long)data[1] << 8U)
        | ((unsigned long long)data[2] << 16U)
        | ((unsigned long long)data[3] << 24U)
        | ((unsigned long long)data[4] << 32U)
        | ((unsigned long long)data[5] << 40U)
        | ((unsigned long long)data[6] << 48U)
        | ((unsigned long long)data[7] << 56U);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_read_bool(const void *data)
{
    return (*(const unsigned char *)data != 0U) ? 1U : 0U;
}

__attribute__((used, noinline))
unsigned int open_cfw_format_bool_write(
    void *output,
    const void *raw_descriptor
)
{
    const unsigned char *descriptor =
        (const unsigned char *)raw_descriptor;
    const unsigned int value =
        open_cfw_format_read_bool(open_cfw_format_scalar_data(descriptor));

    return OPEN_CFW_FORMAT_SCALAR_PREFIX(
        output,
        (unsigned long long)value
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_format_integer_write(
    void *output,
    const void *raw_descriptor
)
{
    const unsigned char *descriptor =
        (const unsigned char *)raw_descriptor;
    const unsigned int length = open_cfw_format_scalar_size(descriptor);
    const unsigned int format_type =
        (unsigned int)(descriptor[0x16] & 0x0FU);
    const unsigned char *data;
    unsigned long long bits;

    if (
        (length != 1U)
        && (length != 2U)
        && (length != 4U)
        && (length != 8U)
    ) {
        OPEN_CFW_FORMAT_SCALAR_SET_INVALID_SIZE(output);
        return 0U;
    }

    data = open_cfw_format_scalar_data(descriptor);
    bits = open_cfw_format_scalar_read_unsigned(data, length);
    if (format_type == 2U) {
        return OPEN_CFW_FORMAT_SCALAR_PREFIX(output, bits);
    }

    if (
        (length < 8U)
        && ((data[length - 1U] & 0x80U) != 0U)
    ) {
        bits |= ~0ULL << (length * 8U);
    }
    if (format_type == 3U) {
        return OPEN_CFW_FORMAT_SCALAR_ZIGZAG(
            output,
            (long long)bits
        );
    }
    return OPEN_CFW_FORMAT_SCALAR_PREFIX(output, bits);
}

__attribute__((used, noinline))
unsigned int open_cfw_format_fixed_write(
    void *output,
    const void *raw_descriptor
)
{
    const unsigned char *descriptor =
        (const unsigned char *)raw_descriptor;
    const unsigned int length = open_cfw_format_scalar_size(descriptor);
    const void *data = open_cfw_format_scalar_data(descriptor);

    if (length == 4U) {
        return OPEN_CFW_FORMAT_SCALAR_FIXED4(output, data);
    }
    if (length == 8U) {
        return OPEN_CFW_FORMAT_SCALAR_FIXED8(output, data);
    }
    OPEN_CFW_FORMAT_SCALAR_SET_INVALID_SIZE(output);
    return 0U;
}
