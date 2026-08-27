#include <stdint.h>
#include <string.h>

typedef void (*open_cfw_test_log_handler_fn)(void *context);

static char open_cfw_test_log_context[64];
static open_cfw_test_log_handler_fn open_cfw_test_log_handler;
static unsigned int open_cfw_test_log_format_calls;
static unsigned int open_cfw_test_log_handler_one_calls;
static unsigned int open_cfw_test_log_handler_two_calls;
static const char *open_cfw_test_log_seen_format;
static void *open_cfw_test_log_seen_cursor;
static void *open_cfw_test_log_seen_context;
static unsigned int open_cfw_test_log_format_result;
static unsigned int open_cfw_test_log_switch_handler;

static void open_cfw_test_log_handler_one(void *context)
{
    open_cfw_test_log_handler_one_calls += 1U;
    open_cfw_test_log_seen_context = context;
}

static void open_cfw_test_log_handler_two(void *context)
{
    open_cfw_test_log_handler_two_calls += 1U;
    open_cfw_test_log_seen_context = context;
}

static unsigned int open_cfw_test_log_vformat(
    char *output,
    const char *format,
    void *argument_cursor
)
{
    open_cfw_test_log_format_calls += 1U;
    open_cfw_test_log_seen_format = format;
    open_cfw_test_log_seen_cursor = argument_cursor;
    memcpy(output, "formatted", sizeof("formatted"));
    if (open_cfw_test_log_switch_handler != 0U) {
        open_cfw_test_log_handler = open_cfw_test_log_handler_two;
    }
    return open_cfw_test_log_format_result;
}

#define OPEN_CFW_BOOTLOADER_LOG_HANDLER() open_cfw_test_log_handler
#define OPEN_CFW_BOOTLOADER_LOG_CONTEXT open_cfw_test_log_context
#define OPEN_CFW_BOOTLOADER_LOG_ARGUMENT_CURSOR(arguments) \
    ((void)sizeof(arguments), (void *)(uintptr_t)0x12345678U)
#define OPEN_CFW_BOOTLOADER_LOG_VFORMAT(output, format, arguments) \
    open_cfw_test_log_vformat((output), (format), (arguments))
#include "../../components/bootloader/core_overlay/runtime_log_dispatch.c"

void open_cfw_test_log_dispatch_reset(void)
{
    memset(open_cfw_test_log_context, 0, sizeof(open_cfw_test_log_context));
    open_cfw_test_log_handler = (open_cfw_test_log_handler_fn)0;
    open_cfw_test_log_format_calls = 0U;
    open_cfw_test_log_handler_one_calls = 0U;
    open_cfw_test_log_handler_two_calls = 0U;
    open_cfw_test_log_seen_format = (const char *)0;
    open_cfw_test_log_seen_cursor = (void *)0;
    open_cfw_test_log_seen_context = (void *)0;
    open_cfw_test_log_format_result = 0U;
    open_cfw_test_log_switch_handler = 0U;
}

void open_cfw_test_log_dispatch_enable(unsigned int switch_handler)
{
    open_cfw_test_log_handler = open_cfw_test_log_handler_one;
    open_cfw_test_log_switch_handler = switch_handler;
}

void open_cfw_test_log_dispatch_set_result(unsigned int result)
{
    open_cfw_test_log_format_result = result;
}

unsigned int open_cfw_test_log_dispatch_run(const char *format)
{
    return open_cfw_bootloader_log_dispatch(format, 0xA5A5A5A5U);
}

unsigned int open_cfw_test_log_dispatch_format_calls(void)
{
    return open_cfw_test_log_format_calls;
}

unsigned int open_cfw_test_log_dispatch_handler_one_calls(void)
{
    return open_cfw_test_log_handler_one_calls;
}

unsigned int open_cfw_test_log_dispatch_handler_two_calls(void)
{
    return open_cfw_test_log_handler_two_calls;
}

const char *open_cfw_test_log_dispatch_seen_format(void)
{
    return open_cfw_test_log_seen_format;
}

void *open_cfw_test_log_dispatch_seen_cursor(void)
{
    return open_cfw_test_log_seen_cursor;
}

void *open_cfw_test_log_dispatch_seen_context(void)
{
    return open_cfw_test_log_seen_context;
}

void *open_cfw_test_log_dispatch_context(void)
{
    return open_cfw_test_log_context;
}

const char *open_cfw_test_log_dispatch_output(void)
{
    return open_cfw_test_log_context;
}
