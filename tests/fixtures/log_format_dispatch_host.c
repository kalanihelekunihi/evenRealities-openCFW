#include <stdint.h>

typedef void (*open_cfw_test_log_format_handler_fn)(void *context);

unsigned int open_cfw_test_log_format_handler_enabled;
unsigned int open_cfw_test_log_format_handler_selection;
unsigned int open_cfw_test_log_format_switch_handler_during_vformat;
unsigned int open_cfw_test_log_format_vformat_result;
unsigned int open_cfw_test_log_format_vformat_calls;
unsigned int open_cfw_test_log_format_handler_calls;
unsigned int open_cfw_test_log_format_last_handler;
unsigned int open_cfw_test_log_format_event_count;
unsigned int open_cfw_test_log_format_events[2];
unsigned int open_cfw_test_log_format_arguments[6];
void *open_cfw_test_log_format_vformat_context;
const char *open_cfw_test_log_format_vformat_format;
void *open_cfw_test_log_format_handler_context;
void *open_cfw_test_log_format_context = (void *)(uintptr_t)0x11223344U;

static void open_cfw_test_log_format_record_handler(
    void *context,
    unsigned int handler_id
)
{
    open_cfw_test_log_format_handler_calls += 1U;
    open_cfw_test_log_format_last_handler = handler_id;
    open_cfw_test_log_format_handler_context = context;
    open_cfw_test_log_format_events[
        open_cfw_test_log_format_event_count
    ] = 2U;
    open_cfw_test_log_format_event_count += 1U;
}

static void open_cfw_test_log_format_handler_one(void *context)
{
    open_cfw_test_log_format_record_handler(context, 1U);
}

static void open_cfw_test_log_format_handler_two(void *context)
{
    open_cfw_test_log_format_record_handler(context, 2U);
}

open_cfw_test_log_format_handler_fn
open_cfw_test_log_format_handler_read(void)
{
    if (open_cfw_test_log_format_handler_enabled == 0U) {
        return (open_cfw_test_log_format_handler_fn)0;
    }
    return open_cfw_test_log_format_handler_selection == 2U
        ? open_cfw_test_log_format_handler_two
        : open_cfw_test_log_format_handler_one;
}

unsigned int open_cfw_test_log_format_vformat(
    void *context,
    const char *format,
    __builtin_va_list arguments
)
{
    unsigned int index;

    open_cfw_test_log_format_vformat_calls += 1U;
    open_cfw_test_log_format_vformat_context = context;
    open_cfw_test_log_format_vformat_format = format;
    open_cfw_test_log_format_events[
        open_cfw_test_log_format_event_count
    ] = 1U;
    open_cfw_test_log_format_event_count += 1U;
    for (index = 0U; index < 6U; index += 1U) {
        open_cfw_test_log_format_arguments[index] =
            __builtin_va_arg(arguments, unsigned int);
    }
    if (open_cfw_test_log_format_switch_handler_during_vformat != 0U) {
        open_cfw_test_log_format_handler_selection = 2U;
    }
    return open_cfw_test_log_format_vformat_result;
}

void open_cfw_test_log_format_reset(void)
{
    unsigned int index;

    open_cfw_test_log_format_handler_enabled = 0U;
    open_cfw_test_log_format_handler_selection = 1U;
    open_cfw_test_log_format_switch_handler_during_vformat = 0U;
    open_cfw_test_log_format_vformat_result = 0U;
    open_cfw_test_log_format_vformat_calls = 0U;
    open_cfw_test_log_format_handler_calls = 0U;
    open_cfw_test_log_format_last_handler = 0U;
    open_cfw_test_log_format_event_count = 0U;
    open_cfw_test_log_format_vformat_context = (void *)0;
    open_cfw_test_log_format_vformat_format = (const char *)0;
    open_cfw_test_log_format_handler_context = (void *)0;
    for (index = 0U; index < 2U; index += 1U) {
        open_cfw_test_log_format_events[index] = 0U;
    }
    for (index = 0U; index < 6U; index += 1U) {
        open_cfw_test_log_format_arguments[index] = 0U;
    }
}

#define OPEN_CFW_LOG_FORMAT_HANDLER() \
    open_cfw_test_log_format_handler_read()
#define OPEN_CFW_LOG_FORMAT_CONTEXT open_cfw_test_log_format_context
#define OPEN_CFW_LOG_FORMAT_ARGUMENT_CURSOR(arguments) (arguments)
#define OPEN_CFW_LOG_FORMAT_VFORMAT(destination, format, arguments) \
    open_cfw_test_log_format_vformat( \
        (destination), \
        (format), \
        (arguments) \
    )

#include "../../components/apollo_main/core_overlay/log_format_dispatch.c"
