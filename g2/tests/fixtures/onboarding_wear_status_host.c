#include <stdarg.h>
#include <stdint.h>

unsigned int open_cfw_test_onboarding_wear_ota_active;
unsigned int open_cfw_test_onboarding_wear_transport_ready;
unsigned int open_cfw_test_onboarding_wear_mode_ready;
int open_cfw_test_onboarding_wear_notify_result;
unsigned int open_cfw_test_onboarding_wear_level_values[8];
unsigned int open_cfw_test_onboarding_wear_level_value_count;

unsigned int open_cfw_test_onboarding_wear_events[24];
unsigned int open_cfw_test_onboarding_wear_event_count;
unsigned int open_cfw_test_onboarding_wear_mode_argument;
unsigned int open_cfw_test_onboarding_wear_notify_command;
unsigned int open_cfw_test_onboarding_wear_notify_event[3];
unsigned int open_cfw_test_onboarding_wear_log_fields[7];
unsigned int open_cfw_test_onboarding_wear_trace_fields[5];
unsigned int open_cfw_test_onboarding_wear_log_calls;
unsigned int open_cfw_test_onboarding_wear_trace_calls;
unsigned int open_cfw_test_onboarding_wear_level_calls;

static void open_cfw_test_onboarding_wear_record(unsigned int event)
{
    open_cfw_test_onboarding_wear_events[
        open_cfw_test_onboarding_wear_event_count++
    ] = event;
}

void open_cfw_test_onboarding_wear_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_wear_ota_active = 0U;
    open_cfw_test_onboarding_wear_transport_ready = 1U;
    open_cfw_test_onboarding_wear_mode_ready = 1U;
    open_cfw_test_onboarding_wear_notify_result = 0;
    open_cfw_test_onboarding_wear_level_value_count = 0U;
    open_cfw_test_onboarding_wear_event_count = 0U;
    open_cfw_test_onboarding_wear_mode_argument = 0U;
    open_cfw_test_onboarding_wear_notify_command = 0U;
    open_cfw_test_onboarding_wear_log_calls = 0U;
    open_cfw_test_onboarding_wear_trace_calls = 0U;
    open_cfw_test_onboarding_wear_level_calls = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_onboarding_wear_level_values[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_onboarding_wear_notify_event[index] = 0U;
    }
    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_onboarding_wear_log_fields[index] = 0U;
    }
    for (index = 0U; index < 5U; ++index) {
        open_cfw_test_onboarding_wear_trace_fields[index] = 0U;
    }
}

static unsigned int open_cfw_test_onboarding_wear_query_ota(void)
{
    open_cfw_test_onboarding_wear_record(1U);
    return open_cfw_test_onboarding_wear_ota_active;
}

static unsigned int open_cfw_test_onboarding_wear_query_transport(void)
{
    open_cfw_test_onboarding_wear_record(2U);
    return open_cfw_test_onboarding_wear_transport_ready;
}

static unsigned int open_cfw_test_onboarding_wear_query_mode(
    unsigned int mode
)
{
    open_cfw_test_onboarding_wear_record(3U);
    open_cfw_test_onboarding_wear_mode_argument = mode;
    return open_cfw_test_onboarding_wear_mode_ready;
}

static int open_cfw_test_onboarding_wear_notify(
    unsigned int command,
    const void *event_pointer
)
{
    const unsigned int *event = event_pointer;

    open_cfw_test_onboarding_wear_record(4U);
    open_cfw_test_onboarding_wear_notify_command = command;
    open_cfw_test_onboarding_wear_notify_event[0] = event[0];
    open_cfw_test_onboarding_wear_notify_event[1] = event[1];
    open_cfw_test_onboarding_wear_notify_event[2] = event[2];
    return open_cfw_test_onboarding_wear_notify_result;
}

static unsigned int open_cfw_test_onboarding_wear_log_level(void)
{
    unsigned int index = open_cfw_test_onboarding_wear_level_calls++;

    open_cfw_test_onboarding_wear_record(5U);
    if (index >= open_cfw_test_onboarding_wear_level_value_count) {
        return 0U;
    }
    return open_cfw_test_onboarding_wear_level_values[index];
}

static void open_cfw_test_onboarding_wear_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    ...
)
{
    va_list arguments;

    open_cfw_test_onboarding_wear_record(6U);
    ++open_cfw_test_onboarding_wear_log_calls;
    open_cfw_test_onboarding_wear_log_fields[0] = level;
    open_cfw_test_onboarding_wear_log_fields[1] =
        (unsigned int)(uintptr_t)module;
    open_cfw_test_onboarding_wear_log_fields[2] =
        (unsigned int)(uintptr_t)file;
    open_cfw_test_onboarding_wear_log_fields[3] =
        (unsigned int)(uintptr_t)function;
    open_cfw_test_onboarding_wear_log_fields[4] = line;
    open_cfw_test_onboarding_wear_log_fields[5] =
        (unsigned int)(uintptr_t)message;
    va_start(arguments, message);
    open_cfw_test_onboarding_wear_log_fields[6] =
        va_arg(arguments, unsigned int);
    va_end(arguments);
}

static void open_cfw_test_onboarding_wear_trace(
    unsigned int level,
    const void *format,
    const void *argument,
    ...
)
{
    va_list arguments;

    open_cfw_test_onboarding_wear_record(7U);
    ++open_cfw_test_onboarding_wear_trace_calls;
    open_cfw_test_onboarding_wear_trace_fields[0] = level;
    open_cfw_test_onboarding_wear_trace_fields[1] =
        (unsigned int)(uintptr_t)format;
    open_cfw_test_onboarding_wear_trace_fields[2] =
        (unsigned int)(uintptr_t)argument;
    va_start(arguments, argument);
    open_cfw_test_onboarding_wear_trace_fields[3] =
        va_arg(arguments, unsigned int);
    va_end(arguments);
}

#define OPEN_CFW_ONBOARDING_WEAR_OTA_ACTIVE() \
    open_cfw_test_onboarding_wear_query_ota()
#define OPEN_CFW_ONBOARDING_WEAR_TRANSPORT_READY() \
    open_cfw_test_onboarding_wear_query_transport()
#define OPEN_CFW_ONBOARDING_WEAR_MODE_READY(mode) \
    open_cfw_test_onboarding_wear_query_mode((mode))
#define OPEN_CFW_ONBOARDING_WEAR_NOTIFY(command, event) \
    open_cfw_test_onboarding_wear_notify((command), (event))
#define OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL() \
    open_cfw_test_onboarding_wear_log_level()
#define OPEN_CFW_ONBOARDING_WEAR_LOG(...) \
    open_cfw_test_onboarding_wear_log(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_WEAR_TRACE(...) \
    open_cfw_test_onboarding_wear_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/onboarding_wear_status.c"
