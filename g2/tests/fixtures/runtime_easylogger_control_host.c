#include <stdint.h>
#include <string.h>

static uint32_t open_cfw_test_easylogger_storage[0xF8U / 4U];
static uint32_t open_cfw_test_easylogger_assert_count;
static uint32_t open_cfw_test_easylogger_assert_line;
static char open_cfw_test_easylogger_assert_expression[96];
static char open_cfw_test_easylogger_assert_function[64];
static uint32_t open_cfw_test_easylogger_port_lock_count;
static uint32_t open_cfw_test_easylogger_port_unlock_count;

static void open_cfw_test_easylogger_copy_string(
    char *destination,
    uint32_t capacity,
    const char *source
)
{
    uint32_t index = 0U;

    if (capacity == 0U) {
        return;
    }
    while ((index + 1U < capacity) && (source[index] != '\0')) {
        destination[index] = source[index];
        index++;
    }
    destination[index] = '\0';
}

static void open_cfw_test_easylogger_assert_failed(
    const char *expression,
    const char *function,
    uint32_t line
)
{
    open_cfw_test_easylogger_assert_count++;
    open_cfw_test_easylogger_assert_line = line;
    open_cfw_test_easylogger_copy_string(
        open_cfw_test_easylogger_assert_expression,
        sizeof(open_cfw_test_easylogger_assert_expression),
        expression
    );
    open_cfw_test_easylogger_copy_string(
        open_cfw_test_easylogger_assert_function,
        sizeof(open_cfw_test_easylogger_assert_function),
        function
    );
}

static char *open_cfw_test_easylogger_filter_copy(
    char *destination,
    const char *source,
    uint32_t count
)
{
    return strncpy(destination, source, count);
}

static void open_cfw_test_easylogger_port_lock(void)
{
    open_cfw_test_easylogger_port_lock_count++;
}

static void open_cfw_test_easylogger_port_unlock(void)
{
    open_cfw_test_easylogger_port_unlock_count++;
}

#define OPEN_CFW_EASYLOGGER_STATE() \
    ((struct open_cfw_easylogger *)open_cfw_test_easylogger_storage)
#define OPEN_CFW_EASYLOGGER_ASSERT_FAILED(expression, function, line) \
    open_cfw_test_easylogger_assert_failed((expression), (function), (line))
#define OPEN_CFW_EASYLOGGER_FILTER_COPY(destination, source, count) \
    open_cfw_test_easylogger_filter_copy((destination), (source), (count))
#define OPEN_CFW_EASYLOGGER_PORT_LOCK() \
    open_cfw_test_easylogger_port_lock()
#define OPEN_CFW_EASYLOGGER_PORT_UNLOCK() \
    open_cfw_test_easylogger_port_unlock()
#include "../../components/apollo_main/core_overlay/runtime_easylogger_control.c"

void open_cfw_test_easylogger_reset(void)
{
    memset(
        open_cfw_test_easylogger_storage,
        0,
        sizeof(open_cfw_test_easylogger_storage)
    );
    open_cfw_test_easylogger_assert_count = 0U;
    open_cfw_test_easylogger_assert_line = 0U;
    open_cfw_test_easylogger_assert_expression[0] = '\0';
    open_cfw_test_easylogger_assert_function[0] = '\0';
    open_cfw_test_easylogger_port_lock_count = 0U;
    open_cfw_test_easylogger_port_unlock_count = 0U;
}

uint32_t open_cfw_test_easylogger_read_u8(uint32_t offset)
{
    return ((const uint8_t *)open_cfw_test_easylogger_storage)[offset];
}

void open_cfw_test_easylogger_write_u8(uint32_t offset, uint32_t value)
{
    ((uint8_t *)open_cfw_test_easylogger_storage)[offset] = (uint8_t)value;
}

uint32_t open_cfw_test_easylogger_read_u32(uint32_t offset)
{
    uint32_t value;

    memcpy(
        &value,
        (const uint8_t *)open_cfw_test_easylogger_storage + offset,
        sizeof(value)
    );
    return value;
}

uint32_t open_cfw_test_easylogger_get_assert_count(void)
{
    return open_cfw_test_easylogger_assert_count;
}

uint32_t open_cfw_test_easylogger_get_assert_line(void)
{
    return open_cfw_test_easylogger_assert_line;
}

const char *open_cfw_test_easylogger_get_assert_expression(void)
{
    return open_cfw_test_easylogger_assert_expression;
}

const char *open_cfw_test_easylogger_get_assert_function(void)
{
    return open_cfw_test_easylogger_assert_function;
}

uint32_t open_cfw_test_easylogger_get_port_lock_count(void)
{
    return open_cfw_test_easylogger_port_lock_count;
}

uint32_t open_cfw_test_easylogger_get_port_unlock_count(void)
{
    return open_cfw_test_easylogger_port_unlock_count;
}
