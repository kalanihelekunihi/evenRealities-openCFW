/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned G2 style-property setter.
 */

static int open_cfw_test_runtime_style_set_is_static(const void *style);
static unsigned int open_cfw_test_runtime_style_set_reallocate(
    unsigned int allocation,
    unsigned int size
);
static unsigned char *open_cfw_test_runtime_style_set_pointer_to_bytes(
    unsigned int value
);
static unsigned char open_cfw_test_runtime_style_set_bucket_index(
    unsigned char property
);
static void open_cfw_test_runtime_style_set_log_constant(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int message
);
static void open_cfw_test_runtime_style_set_log_assert(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int format,
    unsigned int expression
);
static void open_cfw_test_runtime_style_set_fatal(void);

#define OPEN_CFW_RUNTIME_STYLE_SET_IS_STATIC(style) \
    open_cfw_test_runtime_style_set_is_static((style))
#define OPEN_CFW_RUNTIME_STYLE_SET_REALLOCATE(allocation, size) \
    open_cfw_test_runtime_style_set_reallocate((allocation), (size))
#define OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_style_set_pointer_to_bytes((value))
#define OPEN_CFW_RUNTIME_STYLE_SET_BUCKET_INDEX(property) \
    open_cfw_test_runtime_style_set_bucket_index((property))
#define OPEN_CFW_RUNTIME_STYLE_SET_LOG_CONSTANT( \
    level, file, line, function, message \
) \
    open_cfw_test_runtime_style_set_log_constant( \
        (level), (file), (line), (function), (message) \
    )
#define OPEN_CFW_RUNTIME_STYLE_SET_LOG_ASSERT( \
    level, file, line, function, format, expression \
) \
    open_cfw_test_runtime_style_set_log_assert( \
        (level), \
        (file), \
        (line), \
        (function), \
        (format), \
        (expression) \
    )
#define OPEN_CFW_RUNTIME_STYLE_SET_FATAL() \
    open_cfw_test_runtime_style_set_fatal()

#include "../../components/apollo_main/core_overlay/runtime_style_set_property.c"

enum {
    OPEN_CFW_TEST_RUNTIME_STYLE_SET_STORAGE_SIZE = 32768U,
    OPEN_CFW_TEST_RUNTIME_STYLE_SET_OLD_TABLE = 64U,
    OPEN_CFW_TEST_RUNTIME_STYLE_SET_NEW_TABLE = 8192U
};

unsigned char open_cfw_test_runtime_style_set_storage[
    OPEN_CFW_TEST_RUNTIME_STYLE_SET_STORAGE_SIZE
];
struct open_cfw_runtime_style_set_descriptor
    open_cfw_test_runtime_style_set_descriptor;

unsigned int open_cfw_test_runtime_style_set_sequence;
unsigned int open_cfw_test_runtime_style_set_static_calls;
unsigned int open_cfw_test_runtime_style_set_static_order;
unsigned int open_cfw_test_runtime_style_set_reallocate_calls;
unsigned int open_cfw_test_runtime_style_set_reallocate_order;
unsigned int open_cfw_test_runtime_style_set_reallocate_allocation;
unsigned int open_cfw_test_runtime_style_set_reallocate_size;
unsigned int open_cfw_test_runtime_style_set_reallocate_result;
unsigned int open_cfw_test_runtime_style_set_reallocate_table_before;
unsigned int open_cfw_test_runtime_style_set_reallocate_count_before;
unsigned int open_cfw_test_runtime_style_set_pointer_calls;
unsigned int open_cfw_test_runtime_style_set_bucket_calls;
unsigned int open_cfw_test_runtime_style_set_bucket_order;
unsigned int open_cfw_test_runtime_style_set_bucket_property;
unsigned int open_cfw_test_runtime_style_set_bucket_table;
unsigned int open_cfw_test_runtime_style_set_bucket_count;
unsigned int open_cfw_test_runtime_style_set_log_calls;
unsigned int open_cfw_test_runtime_style_set_log_order;
unsigned int open_cfw_test_runtime_style_set_log_level;
unsigned int open_cfw_test_runtime_style_set_log_file;
unsigned int open_cfw_test_runtime_style_set_log_line;
unsigned int open_cfw_test_runtime_style_set_log_function;
unsigned int open_cfw_test_runtime_style_set_log_message;
unsigned int open_cfw_test_runtime_style_set_log_expression;
unsigned int open_cfw_test_runtime_style_set_fatal_calls;
unsigned int open_cfw_test_runtime_style_set_fatal_order;

static int open_cfw_test_runtime_style_set_is_static(
    const void *style_pointer
)
{
    const unsigned char *bytes = (const unsigned char *)style_pointer;

    open_cfw_test_runtime_style_set_sequence += 1U;
    open_cfw_test_runtime_style_set_static_calls += 1U;
    open_cfw_test_runtime_style_set_static_order =
        open_cfw_test_runtime_style_set_sequence;
    return bytes[8] == 0xFFU;
}

static unsigned int open_cfw_test_runtime_style_set_reallocate(
    unsigned int allocation,
    unsigned int size
)
{
    unsigned int old_size;
    unsigned int index;

    open_cfw_test_runtime_style_set_sequence += 1U;
    open_cfw_test_runtime_style_set_reallocate_calls += 1U;
    open_cfw_test_runtime_style_set_reallocate_order =
        open_cfw_test_runtime_style_set_sequence;
    open_cfw_test_runtime_style_set_reallocate_allocation = allocation;
    open_cfw_test_runtime_style_set_reallocate_size = size;
    open_cfw_test_runtime_style_set_reallocate_table_before =
        open_cfw_test_runtime_style_set_descriptor.table;
    open_cfw_test_runtime_style_set_reallocate_count_before =
        open_cfw_test_runtime_style_set_descriptor.count_or_static;

    if (
        open_cfw_test_runtime_style_set_reallocate_result != 0U
        && allocation != 0U
        && open_cfw_test_runtime_style_set_reallocate_result != allocation
    ) {
        old_size =
            open_cfw_test_runtime_style_set_descriptor.count_or_static * 5U;
        for (index = 0U; index < old_size; index += 1U) {
            open_cfw_test_runtime_style_set_storage[
                open_cfw_test_runtime_style_set_reallocate_result + index
            ] = open_cfw_test_runtime_style_set_storage[
                allocation + index
            ];
        }
    }
    return open_cfw_test_runtime_style_set_reallocate_result;
}

static unsigned char *open_cfw_test_runtime_style_set_pointer_to_bytes(
    unsigned int value
)
{
    open_cfw_test_runtime_style_set_pointer_calls += 1U;
    return open_cfw_test_runtime_style_set_storage + value;
}

static unsigned char open_cfw_test_runtime_style_set_bucket_index(
    unsigned char property
)
{
    unsigned char index = (unsigned char)(property >> 2U);

    open_cfw_test_runtime_style_set_sequence += 1U;
    open_cfw_test_runtime_style_set_bucket_calls += 1U;
    open_cfw_test_runtime_style_set_bucket_order =
        open_cfw_test_runtime_style_set_sequence;
    open_cfw_test_runtime_style_set_bucket_property = property;
    open_cfw_test_runtime_style_set_bucket_table =
        open_cfw_test_runtime_style_set_descriptor.table;
    open_cfw_test_runtime_style_set_bucket_count =
        open_cfw_test_runtime_style_set_descriptor.count_or_static;
    if (index > 31U) {
        index = 31U;
    }
    return index;
}

static void open_cfw_test_runtime_style_set_log_constant(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int message
)
{
    open_cfw_test_runtime_style_set_sequence += 1U;
    open_cfw_test_runtime_style_set_log_calls += 1U;
    open_cfw_test_runtime_style_set_log_order =
        open_cfw_test_runtime_style_set_sequence;
    open_cfw_test_runtime_style_set_log_level = level;
    open_cfw_test_runtime_style_set_log_file = file;
    open_cfw_test_runtime_style_set_log_line = line;
    open_cfw_test_runtime_style_set_log_function = function;
    open_cfw_test_runtime_style_set_log_message = message;
    open_cfw_test_runtime_style_set_log_expression = 0U;
}

static void open_cfw_test_runtime_style_set_log_assert(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int format,
    unsigned int expression
)
{
    open_cfw_test_runtime_style_set_log_constant(
        level,
        file,
        line,
        function,
        format
    );
    open_cfw_test_runtime_style_set_log_expression = expression;
}

static void open_cfw_test_runtime_style_set_fatal(void)
{
    open_cfw_test_runtime_style_set_sequence += 1U;
    open_cfw_test_runtime_style_set_fatal_calls += 1U;
    open_cfw_test_runtime_style_set_fatal_order =
        open_cfw_test_runtime_style_set_sequence;
}

static void open_cfw_test_runtime_style_set_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_style_set_storage[offset] =
        (unsigned char)value;
    open_cfw_test_runtime_style_set_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_style_set_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_style_set_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

void open_cfw_test_runtime_style_set_reset(
    unsigned int count_or_static,
    unsigned int table,
    unsigned int reallocate_result
)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_STYLE_SET_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_style_set_storage[index] = 0xCCU;
    }

    open_cfw_test_runtime_style_set_descriptor.table = table;
    open_cfw_test_runtime_style_set_descriptor.property_groups =
        0xA55A3CC3U;
    open_cfw_test_runtime_style_set_descriptor.count_or_static =
        (unsigned char)count_or_static;
    open_cfw_test_runtime_style_set_descriptor.reserved_09 = 0x19U;
    open_cfw_test_runtime_style_set_descriptor.reserved_0a = 0x2AU;
    open_cfw_test_runtime_style_set_descriptor.reserved_0b = 0x3BU;

    open_cfw_test_runtime_style_set_sequence = 0U;
    open_cfw_test_runtime_style_set_static_calls = 0U;
    open_cfw_test_runtime_style_set_static_order = 0U;
    open_cfw_test_runtime_style_set_reallocate_calls = 0U;
    open_cfw_test_runtime_style_set_reallocate_order = 0U;
    open_cfw_test_runtime_style_set_reallocate_allocation = 0U;
    open_cfw_test_runtime_style_set_reallocate_size = 0U;
    open_cfw_test_runtime_style_set_reallocate_result = reallocate_result;
    open_cfw_test_runtime_style_set_reallocate_table_before = 0U;
    open_cfw_test_runtime_style_set_reallocate_count_before = 0U;
    open_cfw_test_runtime_style_set_pointer_calls = 0U;
    open_cfw_test_runtime_style_set_bucket_calls = 0U;
    open_cfw_test_runtime_style_set_bucket_order = 0U;
    open_cfw_test_runtime_style_set_bucket_property = 0U;
    open_cfw_test_runtime_style_set_bucket_table = 0U;
    open_cfw_test_runtime_style_set_bucket_count = 0U;
    open_cfw_test_runtime_style_set_log_calls = 0U;
    open_cfw_test_runtime_style_set_log_order = 0U;
    open_cfw_test_runtime_style_set_log_level = 0U;
    open_cfw_test_runtime_style_set_log_file = 0U;
    open_cfw_test_runtime_style_set_log_line = 0U;
    open_cfw_test_runtime_style_set_log_function = 0U;
    open_cfw_test_runtime_style_set_log_message = 0U;
    open_cfw_test_runtime_style_set_log_expression = 0U;
    open_cfw_test_runtime_style_set_fatal_calls = 0U;
    open_cfw_test_runtime_style_set_fatal_order = 0U;
}

void open_cfw_test_runtime_style_set_set_groups(unsigned int groups)
{
    open_cfw_test_runtime_style_set_descriptor.property_groups = groups;
}

void open_cfw_test_runtime_style_set_set_entry(
    unsigned int index,
    unsigned int value,
    unsigned int property
)
{
    unsigned int count =
        open_cfw_test_runtime_style_set_descriptor.count_or_static;
    unsigned int table =
        open_cfw_test_runtime_style_set_descriptor.table;

    open_cfw_test_runtime_style_set_store_word(
        table + index * 4U,
        value
    );
    open_cfw_test_runtime_style_set_storage[
        table + count * 4U + index
    ] = (unsigned char)property;
}

void open_cfw_test_runtime_style_set_execute(
    unsigned int property,
    unsigned int value
)
{
    open_cfw_runtime_style_set_property(
        &open_cfw_test_runtime_style_set_descriptor,
        property,
        value
    );
}
