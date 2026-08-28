/*
 * SPDX-License-Identifier: MIT
 *
 * Host substitutions for the source-owned G2 style-property removal
 * routine.
 */

static int open_cfw_test_runtime_style_remove_is_static(
    const void *style
);
static unsigned int open_cfw_test_runtime_style_remove_allocate(
    unsigned int size
);
static void open_cfw_test_runtime_style_remove_free(
    unsigned int allocation
);
static unsigned char *open_cfw_test_runtime_style_remove_pointer_to_bytes(
    unsigned int value
);
static void open_cfw_test_runtime_style_remove_log(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int message
);

#define OPEN_CFW_RUNTIME_STYLE_REMOVE_IS_STATIC(style) \
    open_cfw_test_runtime_style_remove_is_static((style))
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_ALLOCATE(size) \
    open_cfw_test_runtime_style_remove_allocate((size))
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE(allocation) \
    open_cfw_test_runtime_style_remove_free((allocation))
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES(value) \
    open_cfw_test_runtime_style_remove_pointer_to_bytes((value))
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG( \
    level, file, line, function, message \
) \
    open_cfw_test_runtime_style_remove_log( \
        (level), (file), (line), (function), (message) \
    )

#include "../../components/apollo_main/core_overlay/runtime_style_remove_property.c"

enum {
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_STORAGE_SIZE = 32768U,
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_OLD_TABLE = 64U,
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_NEW_TABLE = 8192U,
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_SNAPSHOT_SIZE = 1270U
};

unsigned char open_cfw_test_runtime_style_remove_storage[
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_STORAGE_SIZE
];
unsigned char open_cfw_test_runtime_style_remove_free_snapshot[
    OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_SNAPSHOT_SIZE
];
struct open_cfw_runtime_style_remove_descriptor
    open_cfw_test_runtime_style_remove_descriptor;

unsigned int open_cfw_test_runtime_style_remove_sequence;
unsigned int open_cfw_test_runtime_style_remove_static_calls;
unsigned int open_cfw_test_runtime_style_remove_static_order;
unsigned int open_cfw_test_runtime_style_remove_allocate_calls;
unsigned int open_cfw_test_runtime_style_remove_allocate_order;
unsigned int open_cfw_test_runtime_style_remove_allocate_size;
unsigned int open_cfw_test_runtime_style_remove_allocate_result;
unsigned int open_cfw_test_runtime_style_remove_allocate_table_before;
unsigned int open_cfw_test_runtime_style_remove_allocate_count_before;
unsigned int open_cfw_test_runtime_style_remove_free_calls;
unsigned int open_cfw_test_runtime_style_remove_free_order;
unsigned int open_cfw_test_runtime_style_remove_free_allocation;
unsigned int open_cfw_test_runtime_style_remove_free_table;
unsigned int open_cfw_test_runtime_style_remove_free_count;
unsigned int open_cfw_test_runtime_style_remove_log_calls;
unsigned int open_cfw_test_runtime_style_remove_log_order;
unsigned int open_cfw_test_runtime_style_remove_log_level;
unsigned int open_cfw_test_runtime_style_remove_log_file;
unsigned int open_cfw_test_runtime_style_remove_log_line;
unsigned int open_cfw_test_runtime_style_remove_log_function;
unsigned int open_cfw_test_runtime_style_remove_log_message;
unsigned int open_cfw_test_runtime_style_remove_pointer_calls;

static int open_cfw_test_runtime_style_remove_is_static(
    const void *style_pointer
)
{
    const unsigned char *bytes = (const unsigned char *)style_pointer;

    open_cfw_test_runtime_style_remove_sequence += 1U;
    open_cfw_test_runtime_style_remove_static_calls += 1U;
    open_cfw_test_runtime_style_remove_static_order =
        open_cfw_test_runtime_style_remove_sequence;
    return bytes[8] == 0xFFU;
}

static unsigned int open_cfw_test_runtime_style_remove_allocate(
    unsigned int size
)
{
    open_cfw_test_runtime_style_remove_sequence += 1U;
    open_cfw_test_runtime_style_remove_allocate_calls += 1U;
    open_cfw_test_runtime_style_remove_allocate_order =
        open_cfw_test_runtime_style_remove_sequence;
    open_cfw_test_runtime_style_remove_allocate_size = size;
    open_cfw_test_runtime_style_remove_allocate_table_before =
        open_cfw_test_runtime_style_remove_descriptor.table;
    open_cfw_test_runtime_style_remove_allocate_count_before =
        open_cfw_test_runtime_style_remove_descriptor.count_or_static;
    return open_cfw_test_runtime_style_remove_allocate_result;
}

static void open_cfw_test_runtime_style_remove_free(
    unsigned int allocation
)
{
    unsigned int index;

    open_cfw_test_runtime_style_remove_sequence += 1U;
    open_cfw_test_runtime_style_remove_free_calls += 1U;
    open_cfw_test_runtime_style_remove_free_order =
        open_cfw_test_runtime_style_remove_sequence;
    open_cfw_test_runtime_style_remove_free_allocation = allocation;
    open_cfw_test_runtime_style_remove_free_table =
        open_cfw_test_runtime_style_remove_descriptor.table;
    open_cfw_test_runtime_style_remove_free_count =
        open_cfw_test_runtime_style_remove_descriptor.count_or_static;
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_SNAPSHOT_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_style_remove_free_snapshot[index] =
            open_cfw_test_runtime_style_remove_storage[
                OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_NEW_TABLE + index
            ];
    }
}

static unsigned char *open_cfw_test_runtime_style_remove_pointer_to_bytes(
    unsigned int value
)
{
    open_cfw_test_runtime_style_remove_pointer_calls += 1U;
    return open_cfw_test_runtime_style_remove_storage + value;
}

static void open_cfw_test_runtime_style_remove_log(
    unsigned int level,
    unsigned int file,
    unsigned int line,
    unsigned int function,
    unsigned int message
)
{
    open_cfw_test_runtime_style_remove_sequence += 1U;
    open_cfw_test_runtime_style_remove_log_calls += 1U;
    open_cfw_test_runtime_style_remove_log_order =
        open_cfw_test_runtime_style_remove_sequence;
    open_cfw_test_runtime_style_remove_log_level = level;
    open_cfw_test_runtime_style_remove_log_file = file;
    open_cfw_test_runtime_style_remove_log_line = line;
    open_cfw_test_runtime_style_remove_log_function = function;
    open_cfw_test_runtime_style_remove_log_message = message;
}

static void open_cfw_test_runtime_style_remove_store_word(
    unsigned int offset,
    unsigned int value
)
{
    open_cfw_test_runtime_style_remove_storage[offset] =
        (unsigned char)value;
    open_cfw_test_runtime_style_remove_storage[offset + 1U] =
        (unsigned char)(value >> 8U);
    open_cfw_test_runtime_style_remove_storage[offset + 2U] =
        (unsigned char)(value >> 16U);
    open_cfw_test_runtime_style_remove_storage[offset + 3U] =
        (unsigned char)(value >> 24U);
}

void open_cfw_test_runtime_style_remove_reset(
    unsigned int count_or_static,
    unsigned int allocation_result
)
{
    unsigned int index;

    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_STORAGE_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_style_remove_storage[index] = 0xCCU;
    }
    for (
        index = 0U;
        index < OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_SNAPSHOT_SIZE;
        index += 1U
    ) {
        open_cfw_test_runtime_style_remove_free_snapshot[index] = 0U;
    }

    open_cfw_test_runtime_style_remove_descriptor.table =
        OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_OLD_TABLE;
    open_cfw_test_runtime_style_remove_descriptor.property_groups =
        0xA55A3CC3U;
    open_cfw_test_runtime_style_remove_descriptor.count_or_static =
        (unsigned char)count_or_static;
    open_cfw_test_runtime_style_remove_descriptor.reserved_09 = 0x19U;
    open_cfw_test_runtime_style_remove_descriptor.reserved_0a = 0x2AU;
    open_cfw_test_runtime_style_remove_descriptor.reserved_0b = 0x3BU;

    open_cfw_test_runtime_style_remove_sequence = 0U;
    open_cfw_test_runtime_style_remove_static_calls = 0U;
    open_cfw_test_runtime_style_remove_static_order = 0U;
    open_cfw_test_runtime_style_remove_allocate_calls = 0U;
    open_cfw_test_runtime_style_remove_allocate_order = 0U;
    open_cfw_test_runtime_style_remove_allocate_size = 0U;
    open_cfw_test_runtime_style_remove_allocate_result = allocation_result;
    open_cfw_test_runtime_style_remove_allocate_table_before = 0U;
    open_cfw_test_runtime_style_remove_allocate_count_before = 0U;
    open_cfw_test_runtime_style_remove_free_calls = 0U;
    open_cfw_test_runtime_style_remove_free_order = 0U;
    open_cfw_test_runtime_style_remove_free_allocation = 0U;
    open_cfw_test_runtime_style_remove_free_table = 0U;
    open_cfw_test_runtime_style_remove_free_count = 0U;
    open_cfw_test_runtime_style_remove_log_calls = 0U;
    open_cfw_test_runtime_style_remove_log_order = 0U;
    open_cfw_test_runtime_style_remove_log_level = 0U;
    open_cfw_test_runtime_style_remove_log_file = 0U;
    open_cfw_test_runtime_style_remove_log_line = 0U;
    open_cfw_test_runtime_style_remove_log_function = 0U;
    open_cfw_test_runtime_style_remove_log_message = 0U;
    open_cfw_test_runtime_style_remove_pointer_calls = 0U;
}

void open_cfw_test_runtime_style_remove_set_entry(
    unsigned int index,
    unsigned int value,
    unsigned int property
)
{
    unsigned int count =
        open_cfw_test_runtime_style_remove_descriptor.count_or_static;

    open_cfw_test_runtime_style_remove_store_word(
        OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_OLD_TABLE + index * 4U,
        value
    );
    open_cfw_test_runtime_style_remove_storage[
        OPEN_CFW_TEST_RUNTIME_STYLE_REMOVE_OLD_TABLE
        + count * 4U
        + index
    ] = (unsigned char)property;
}

unsigned int open_cfw_test_runtime_style_remove_execute(
    unsigned int property
)
{
    return open_cfw_runtime_style_remove_property(
        &open_cfw_test_runtime_style_remove_descriptor,
        property
    );
}
