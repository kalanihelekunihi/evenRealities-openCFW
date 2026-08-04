#include <stdint.h>

unsigned int open_cfw_test_onboarding_flag_pending;
int open_cfw_test_onboarding_flag_save_result;
unsigned int open_cfw_test_onboarding_flag_level_values[12];
unsigned int open_cfw_test_onboarding_flag_level_value_count;

unsigned int open_cfw_test_onboarding_flag_events[24];
unsigned int open_cfw_test_onboarding_flag_event_count;
unsigned int open_cfw_test_onboarding_flag_level_calls;
unsigned int open_cfw_test_onboarding_flag_log_calls;
unsigned int open_cfw_test_onboarding_flag_trace_calls;
unsigned int open_cfw_test_onboarding_flag_save_calls;
unsigned int open_cfw_test_onboarding_flag_pending_seen_by_save;
unsigned int open_cfw_test_onboarding_flag_log_fields[6];
unsigned int open_cfw_test_onboarding_flag_trace_fields[3];

static void open_cfw_test_onboarding_flag_record(unsigned int event)
{
    open_cfw_test_onboarding_flag_events[
        open_cfw_test_onboarding_flag_event_count++
    ] = event;
}

void open_cfw_test_onboarding_flag_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_flag_pending = 1U;
    open_cfw_test_onboarding_flag_save_result = 0;
    open_cfw_test_onboarding_flag_level_value_count = 0U;
    open_cfw_test_onboarding_flag_event_count = 0U;
    open_cfw_test_onboarding_flag_level_calls = 0U;
    open_cfw_test_onboarding_flag_log_calls = 0U;
    open_cfw_test_onboarding_flag_trace_calls = 0U;
    open_cfw_test_onboarding_flag_save_calls = 0U;
    open_cfw_test_onboarding_flag_pending_seen_by_save = 0U;
    for (index = 0U; index < 12U; ++index) {
        open_cfw_test_onboarding_flag_level_values[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_onboarding_flag_log_fields[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_onboarding_flag_trace_fields[index] = 0U;
    }
}

static int open_cfw_test_onboarding_flag_save(void)
{
    open_cfw_test_onboarding_flag_record(4U);
    ++open_cfw_test_onboarding_flag_save_calls;
    open_cfw_test_onboarding_flag_pending_seen_by_save =
        open_cfw_test_onboarding_flag_pending;
    return open_cfw_test_onboarding_flag_save_result;
}

static unsigned int open_cfw_test_onboarding_flag_log_level(void)
{
    unsigned int index = open_cfw_test_onboarding_flag_level_calls++;

    open_cfw_test_onboarding_flag_record(1U);
    if (index >= open_cfw_test_onboarding_flag_level_value_count) {
        return 0U;
    }
    return open_cfw_test_onboarding_flag_level_values[index];
}

static void open_cfw_test_onboarding_flag_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message
)
{
    open_cfw_test_onboarding_flag_record(2U);
    ++open_cfw_test_onboarding_flag_log_calls;
    open_cfw_test_onboarding_flag_log_fields[0] = level;
    open_cfw_test_onboarding_flag_log_fields[1] =
        (unsigned int)(uintptr_t)module;
    open_cfw_test_onboarding_flag_log_fields[2] =
        (unsigned int)(uintptr_t)file;
    open_cfw_test_onboarding_flag_log_fields[3] =
        (unsigned int)(uintptr_t)function;
    open_cfw_test_onboarding_flag_log_fields[4] = line;
    open_cfw_test_onboarding_flag_log_fields[5] =
        (unsigned int)(uintptr_t)message;
}

static void open_cfw_test_onboarding_flag_trace(
    unsigned int level,
    const void *format,
    const void *argument
)
{
    open_cfw_test_onboarding_flag_record(3U);
    ++open_cfw_test_onboarding_flag_trace_calls;
    open_cfw_test_onboarding_flag_trace_fields[0] = level;
    open_cfw_test_onboarding_flag_trace_fields[1] =
        (unsigned int)(uintptr_t)format;
    open_cfw_test_onboarding_flag_trace_fields[2] =
        (unsigned int)(uintptr_t)argument;
}

#define OPEN_CFW_ONBOARDING_FLAG_PENDING \
    open_cfw_test_onboarding_flag_pending
#define OPEN_CFW_ONBOARDING_FLAG_SAVE() \
    open_cfw_test_onboarding_flag_save()
#define OPEN_CFW_ONBOARDING_FLAG_LOG_LEVEL() \
    open_cfw_test_onboarding_flag_log_level()
#define OPEN_CFW_ONBOARDING_FLAG_LOG(...) \
    open_cfw_test_onboarding_flag_log(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_FLAG_TRACE(...) \
    open_cfw_test_onboarding_flag_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/onboarding_flag_persist.c"
