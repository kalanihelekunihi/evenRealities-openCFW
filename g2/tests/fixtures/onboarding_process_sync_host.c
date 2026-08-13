#include <stdint.h>
#include <string.h>

int open_cfw_test_onboarding_process_sync_send_result;
unsigned int open_cfw_test_onboarding_process_sync_level_values[8];
unsigned int open_cfw_test_onboarding_process_sync_level_value_count;
unsigned int open_cfw_test_onboarding_process_sync_events[16];
unsigned int open_cfw_test_onboarding_process_sync_event_count;
unsigned int open_cfw_test_onboarding_process_sync_zero_calls;
unsigned int open_cfw_test_onboarding_process_sync_zero_fields[2];
unsigned int open_cfw_test_onboarding_process_sync_send_calls;
unsigned int open_cfw_test_onboarding_process_sync_send_fields[5];
unsigned int open_cfw_test_onboarding_process_sync_payload[3];
unsigned int open_cfw_test_onboarding_process_sync_level_calls;
unsigned int open_cfw_test_onboarding_process_sync_log_calls;
unsigned int open_cfw_test_onboarding_process_sync_log_fields[8];
unsigned int open_cfw_test_onboarding_process_sync_trace_calls;
unsigned int open_cfw_test_onboarding_process_sync_trace_fields[5];
unsigned int open_cfw_test_onboarding_process_sync_mutate_on_send;
unsigned char open_cfw_test_onboarding_process_sync_state[2];
unsigned char open_cfw_test_onboarding_process_sync_send_state[2];

static void open_cfw_test_onboarding_process_sync_record(unsigned int event)
{
    open_cfw_test_onboarding_process_sync_events[
        open_cfw_test_onboarding_process_sync_event_count++
    ] = event;
}

void open_cfw_test_onboarding_process_sync_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_process_sync_send_result = 0;
    open_cfw_test_onboarding_process_sync_level_value_count = 0U;
    open_cfw_test_onboarding_process_sync_event_count = 0U;
    open_cfw_test_onboarding_process_sync_zero_calls = 0U;
    open_cfw_test_onboarding_process_sync_send_calls = 0U;
    open_cfw_test_onboarding_process_sync_level_calls = 0U;
    open_cfw_test_onboarding_process_sync_log_calls = 0U;
    open_cfw_test_onboarding_process_sync_trace_calls = 0U;
    open_cfw_test_onboarding_process_sync_mutate_on_send = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_onboarding_process_sync_level_values[index] = 0U;
        open_cfw_test_onboarding_process_sync_log_fields[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_onboarding_process_sync_events[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_onboarding_process_sync_zero_fields[index] = 0U;
        open_cfw_test_onboarding_process_sync_state[index] = 0U;
        open_cfw_test_onboarding_process_sync_send_state[index] = 0U;
    }
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_onboarding_process_sync_payload[index] = 0U;
    }
    for (index = 0U; index < 5U; ++index) {
        open_cfw_test_onboarding_process_sync_send_fields[index] = 0U;
        open_cfw_test_onboarding_process_sync_trace_fields[index] = 0U;
    }
}

static void *open_cfw_test_onboarding_process_sync_zero(
    void *buffer,
    unsigned int size,
    unsigned int value
)
{
    open_cfw_test_onboarding_process_sync_record(1U);
    ++open_cfw_test_onboarding_process_sync_zero_calls;
    open_cfw_test_onboarding_process_sync_zero_fields[0] = size;
    open_cfw_test_onboarding_process_sync_zero_fields[1] = value;
    memset(buffer, (int)(value & 0xFFU), size);
    return buffer;
}

static int open_cfw_test_onboarding_process_sync_send(
    unsigned int service,
    const void *payload,
    unsigned int size,
    unsigned int context,
    unsigned int mode
)
{
    const unsigned char *bytes = (const unsigned char *)payload;
    unsigned int index;

    open_cfw_test_onboarding_process_sync_record(2U);
    ++open_cfw_test_onboarding_process_sync_send_calls;
    open_cfw_test_onboarding_process_sync_send_fields[0] = service;
    open_cfw_test_onboarding_process_sync_send_fields[1] =
        (unsigned int)(uintptr_t)payload;
    open_cfw_test_onboarding_process_sync_send_fields[2] = size;
    open_cfw_test_onboarding_process_sync_send_fields[3] = context;
    open_cfw_test_onboarding_process_sync_send_fields[4] = mode;
    for (index = 0U; index < 3U; ++index) {
        open_cfw_test_onboarding_process_sync_payload[index] = bytes[index];
    }
    if (open_cfw_test_onboarding_process_sync_mutate_on_send != 0U) {
        open_cfw_test_onboarding_process_sync_state[0] =
            open_cfw_test_onboarding_process_sync_send_state[0];
        open_cfw_test_onboarding_process_sync_state[1] =
            open_cfw_test_onboarding_process_sync_send_state[1];
    }
    return open_cfw_test_onboarding_process_sync_send_result;
}

static unsigned int open_cfw_test_onboarding_process_sync_log_level(void)
{
    unsigned int index = open_cfw_test_onboarding_process_sync_level_calls++;

    open_cfw_test_onboarding_process_sync_record(3U);
    if (index >= open_cfw_test_onboarding_process_sync_level_value_count) {
        return 0U;
    }
    return open_cfw_test_onboarding_process_sync_level_values[index];
}

static void open_cfw_test_onboarding_process_sync_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int process_id,
    unsigned int substep
)
{
    open_cfw_test_onboarding_process_sync_record(4U);
    ++open_cfw_test_onboarding_process_sync_log_calls;
    open_cfw_test_onboarding_process_sync_log_fields[0] = level;
    open_cfw_test_onboarding_process_sync_log_fields[1] =
        (unsigned int)(uintptr_t)module;
    open_cfw_test_onboarding_process_sync_log_fields[2] =
        (unsigned int)(uintptr_t)file;
    open_cfw_test_onboarding_process_sync_log_fields[3] =
        (unsigned int)(uintptr_t)function;
    open_cfw_test_onboarding_process_sync_log_fields[4] = line;
    open_cfw_test_onboarding_process_sync_log_fields[5] =
        (unsigned int)(uintptr_t)message;
    open_cfw_test_onboarding_process_sync_log_fields[6] = process_id;
    open_cfw_test_onboarding_process_sync_log_fields[7] = substep;
}

static void open_cfw_test_onboarding_process_sync_trace(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int process_id,
    unsigned int substep
)
{
    open_cfw_test_onboarding_process_sync_record(5U);
    ++open_cfw_test_onboarding_process_sync_trace_calls;
    open_cfw_test_onboarding_process_sync_trace_fields[0] = level;
    open_cfw_test_onboarding_process_sync_trace_fields[1] =
        (unsigned int)(uintptr_t)format;
    open_cfw_test_onboarding_process_sync_trace_fields[2] =
        (unsigned int)(uintptr_t)argument;
    open_cfw_test_onboarding_process_sync_trace_fields[3] = process_id;
    open_cfw_test_onboarding_process_sync_trace_fields[4] = substep;
}

#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_ZERO(buffer, size, value) \
    open_cfw_test_onboarding_process_sync_zero(buffer, size, value)
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_SEND(...) \
    open_cfw_test_onboarding_process_sync_send(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL() \
    open_cfw_test_onboarding_process_sync_log_level()
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG(...) \
    open_cfw_test_onboarding_process_sync_log(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_TRACE(...) \
    open_cfw_test_onboarding_process_sync_trace(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_STATE() \
    open_cfw_test_onboarding_process_sync_state

#include "../../components/apollo_main/core_overlay/onboarding_process_sync.c"
