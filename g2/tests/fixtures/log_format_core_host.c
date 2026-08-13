#include <stdint.h>
#include <string.h>

enum {
    OPEN_CFW_TEST_LOG_CORE_U32 = 1,
    OPEN_CFW_TEST_LOG_CORE_U64 = 2,
    OPEN_CFW_TEST_LOG_CORE_POINTER = 3,
    OPEN_CFW_TEST_LOG_CORE_DOUBLE = 4
};

typedef struct {
    unsigned int kind;
    unsigned int low;
    unsigned int high;
    const void *pointer;
    double double_value;
} open_cfw_test_log_core_entry;

typedef struct {
    open_cfw_test_log_core_entry entries[32];
    unsigned int count;
    unsigned int index;
    unsigned int error;
} open_cfw_test_log_core_cursor;

open_cfw_test_log_core_cursor open_cfw_test_log_core_arguments;
unsigned int open_cfw_test_log_core_crlf_enabled;
unsigned int open_cfw_test_log_core_float_calls;
unsigned int open_cfw_test_log_core_float_precision;
unsigned int open_cfw_test_log_core_float_capacity;
float open_cfw_test_log_core_float_value;
int open_cfw_test_log_core_float_result;
char open_cfw_test_log_core_float_text[32];

void open_cfw_test_log_core_reset(void)
{
    memset(&open_cfw_test_log_core_arguments, 0, sizeof(
        open_cfw_test_log_core_arguments
    ));
    open_cfw_test_log_core_crlf_enabled = 0U;
    open_cfw_test_log_core_float_calls = 0U;
    open_cfw_test_log_core_float_precision = 0U;
    open_cfw_test_log_core_float_capacity = 0U;
    open_cfw_test_log_core_float_value = 0.0F;
    open_cfw_test_log_core_float_result = 0;
    memset(
        open_cfw_test_log_core_float_text,
        0,
        sizeof(open_cfw_test_log_core_float_text)
    );
}

static open_cfw_test_log_core_entry *
open_cfw_test_log_core_append(unsigned int kind)
{
    open_cfw_test_log_core_entry *entry =
        &open_cfw_test_log_core_arguments.entries[
            open_cfw_test_log_core_arguments.count
        ];

    open_cfw_test_log_core_arguments.count += 1U;
    entry->kind = kind;
    return entry;
}

void open_cfw_test_log_core_push_u32(unsigned int value)
{
    open_cfw_test_log_core_entry *entry = open_cfw_test_log_core_append(
        OPEN_CFW_TEST_LOG_CORE_U32
    );

    entry->low = value;
}

void open_cfw_test_log_core_push_u64(
    unsigned int low,
    unsigned int high
)
{
    open_cfw_test_log_core_entry *entry = open_cfw_test_log_core_append(
        OPEN_CFW_TEST_LOG_CORE_U64
    );

    entry->low = low;
    entry->high = high;
}

void open_cfw_test_log_core_push_pointer(const void *pointer)
{
    open_cfw_test_log_core_entry *entry = open_cfw_test_log_core_append(
        OPEN_CFW_TEST_LOG_CORE_POINTER
    );

    entry->pointer = pointer;
}

void open_cfw_test_log_core_push_double(double value)
{
    open_cfw_test_log_core_entry *entry = open_cfw_test_log_core_append(
        OPEN_CFW_TEST_LOG_CORE_DOUBLE
    );

    entry->double_value = value;
}

static open_cfw_test_log_core_entry *
open_cfw_test_log_core_take(
    unsigned char *cursor,
    unsigned int expected_kind
)
{
    open_cfw_test_log_core_cursor *state =
        (open_cfw_test_log_core_cursor *)(void *)cursor;
    open_cfw_test_log_core_entry *entry;

    if (state->index >= state->count) {
        state->error = 1U;
        return &state->entries[0];
    }
    entry = &state->entries[state->index];
    state->index += 1U;
    if (entry->kind != expected_kind) {
        state->error = 1U;
    }
    return entry;
}

unsigned int open_cfw_test_log_core_read_u32(unsigned char *cursor)
{
    return open_cfw_test_log_core_take(
        cursor,
        OPEN_CFW_TEST_LOG_CORE_U32
    )->low;
}

const char *open_cfw_test_log_core_read_pointer(unsigned char *cursor)
{
    return (const char *)open_cfw_test_log_core_take(
        cursor,
        OPEN_CFW_TEST_LOG_CORE_POINTER
    )->pointer;
}

double open_cfw_test_log_core_read_double(unsigned char *cursor)
{
    return open_cfw_test_log_core_take(
        cursor,
        OPEN_CFW_TEST_LOG_CORE_DOUBLE
    )->double_value;
}

int open_cfw_test_log_core_float_write(
    char *destination,
    unsigned int precision,
    float value
)
{
    open_cfw_test_log_core_float_calls += 1U;
    open_cfw_test_log_core_float_precision = precision;
    open_cfw_test_log_core_float_capacity =
        (unsigned int)(unsigned char)destination[0]
        | ((unsigned int)(unsigned char)destination[1] << 8U)
        | ((unsigned int)(unsigned char)destination[2] << 16U)
        | ((unsigned int)(unsigned char)destination[3] << 24U);
    open_cfw_test_log_core_float_value = value;
    if (open_cfw_test_log_core_float_result >= 0) {
        memcpy(
            destination,
            open_cfw_test_log_core_float_text,
            (unsigned int)open_cfw_test_log_core_float_result + 1U
        );
    }
    return open_cfw_test_log_core_float_result;
}

#define OPEN_CFW_LOG_CORE_CRLF_ENABLED() \
    open_cfw_test_log_core_crlf_enabled
#define OPEN_CFW_LOG_CORE_READ_U32(cursor) \
    open_cfw_test_log_core_read_u32(cursor)
#define OPEN_CFW_LOG_CORE_READ_POINTER(cursor) \
    open_cfw_test_log_core_read_pointer(cursor)
#define OPEN_CFW_LOG_CORE_READ_U64(cursor) \
    (*(open_cfw_log_core_u64_words *)(void *)&open_cfw_test_log_core_take( \
        (cursor), \
        OPEN_CFW_TEST_LOG_CORE_U64 \
    )->low)
#define OPEN_CFW_LOG_CORE_READ_DOUBLE(cursor) \
    open_cfw_test_log_core_read_double(cursor)
#define OPEN_CFW_LOG_CORE_CONVERT_DOUBLE(value) ((float)(value))
#define OPEN_CFW_LOG_CORE_FLOAT_WRITE(destination, precision, value) \
    open_cfw_test_log_core_float_write(destination, precision, value)

#include "../../components/apollo_main/core_overlay/log_format_helpers.c"
#include "../../components/apollo_main/core_overlay/log_format_core.c"

unsigned int open_cfw_test_log_core_run(
    char *destination,
    const char *format
)
{
    return open_cfw_log_format_core(
        destination,
        format,
        &open_cfw_test_log_core_arguments
    );
}

unsigned int open_cfw_test_log_core_argument_count(void)
{
    return open_cfw_test_log_core_arguments.count;
}

unsigned int open_cfw_test_log_core_argument_index(void)
{
    return open_cfw_test_log_core_arguments.index;
}

unsigned int open_cfw_test_log_core_argument_error(void)
{
    return open_cfw_test_log_core_arguments.error;
}
