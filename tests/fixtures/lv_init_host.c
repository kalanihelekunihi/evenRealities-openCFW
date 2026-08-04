#include <stdarg.h>
#include <stdint.h>

volatile unsigned char open_cfw_test_lv_init_global[0x1EC];
volatile unsigned char open_cfw_test_lv_init_utf8_text[3];
unsigned char open_cfw_test_lv_init_endian_first_byte;

unsigned int open_cfw_test_lv_init_global_calls;
void *open_cfw_test_lv_init_global_pointer;
unsigned int open_cfw_test_lv_init_step_calls;
uintptr_t open_cfw_test_lv_init_step_addresses[20];
unsigned int open_cfw_test_lv_init_step_first[20];
unsigned int open_cfw_test_lv_init_step_second[20];
unsigned int open_cfw_test_lv_init_log_calls;
unsigned int open_cfw_test_lv_init_log_level;
const void *open_cfw_test_lv_init_log_file;
unsigned int open_cfw_test_lv_init_log_line;
const void *open_cfw_test_lv_init_log_function;
const void *open_cfw_test_lv_init_log_arguments[3];
unsigned int open_cfw_test_lv_init_fatal_calls;

void open_cfw_test_lv_init_global_initialize(void *global)
{
    open_cfw_test_lv_init_global_calls += 1U;
    open_cfw_test_lv_init_global_pointer = global;
}

static void open_cfw_test_lv_init_record(
    uintptr_t address,
    unsigned int first,
    unsigned int second
)
{
    unsigned int index = open_cfw_test_lv_init_step_calls++;

    if (index < 20U) {
        open_cfw_test_lv_init_step_addresses[index] = address;
        open_cfw_test_lv_init_step_first[index] = first;
        open_cfw_test_lv_init_step_second[index] = second;
    }
}

void open_cfw_test_lv_init_call0(uintptr_t address)
{
    open_cfw_test_lv_init_record(address, 0U, 0U);
}

void open_cfw_test_lv_init_call1(uintptr_t address, unsigned int value)
{
    open_cfw_test_lv_init_record(address, value, 0U);
}

void open_cfw_test_lv_init_call2(
    uintptr_t address,
    unsigned int first,
    unsigned int second
)
{
    open_cfw_test_lv_init_record(address, first, second);
}

void open_cfw_test_lv_init_log(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
)
{
    va_list arguments;
    unsigned int count = line == 0x135U ? 3U : 1U;
    unsigned int index;

    open_cfw_test_lv_init_log_calls += 1U;
    open_cfw_test_lv_init_log_level = level;
    open_cfw_test_lv_init_log_file = file;
    open_cfw_test_lv_init_log_line = line;
    open_cfw_test_lv_init_log_function = function;
    va_start(arguments, function);
    for (index = 0U; index < count; index += 1U) {
        open_cfw_test_lv_init_log_arguments[index] =
            va_arg(arguments, const void *);
    }
    va_end(arguments);
}

void open_cfw_test_lv_init_fatal(void)
{
    open_cfw_test_lv_init_fatal_calls += 1U;
}

#define OPEN_CFW_LV_INIT_GLOBAL open_cfw_test_lv_init_global
#define OPEN_CFW_LV_INIT_GLOBAL_INITIALIZE(global) \
    open_cfw_test_lv_init_global_initialize((void *)(global))
#define OPEN_CFW_LV_INIT_CALL0(address) \
    open_cfw_test_lv_init_call0(address)
#define OPEN_CFW_LV_INIT_CALL1(address, value) \
    open_cfw_test_lv_init_call1((address), (value))
#define OPEN_CFW_LV_INIT_CALL2(address, first, second) \
    open_cfw_test_lv_init_call2((address), (first), (second))
#define OPEN_CFW_LV_INIT_LOG open_cfw_test_lv_init_log
#define OPEN_CFW_LV_INIT_FATAL() open_cfw_test_lv_init_fatal()
#define OPEN_CFW_LV_INIT_UTF8_TEXT open_cfw_test_lv_init_utf8_text
#define OPEN_CFW_LV_INIT_ENDIAN_FIRST_BYTE() \
    open_cfw_test_lv_init_endian_first_byte

#include "../../components/apollo_main/core_overlay/lv_init.c"
