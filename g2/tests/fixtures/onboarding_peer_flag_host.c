#include <stdint.h>
#include <string.h>

unsigned int open_cfw_test_onboarding_peer_flag_value;
int open_cfw_test_onboarding_peer_flag_send_result;
unsigned int open_cfw_test_onboarding_peer_flag_level_values[8];
unsigned int open_cfw_test_onboarding_peer_flag_level_value_count;

unsigned int open_cfw_test_onboarding_peer_flag_events[16];
unsigned int open_cfw_test_onboarding_peer_flag_event_count;
unsigned int open_cfw_test_onboarding_peer_flag_get_calls;
unsigned int open_cfw_test_onboarding_peer_flag_zero_calls;
unsigned int open_cfw_test_onboarding_peer_flag_zero_size;
unsigned int open_cfw_test_onboarding_peer_flag_zero_value;
unsigned int open_cfw_test_onboarding_peer_flag_send_calls;
unsigned int open_cfw_test_onboarding_peer_flag_send_fields[5];
unsigned int open_cfw_test_onboarding_peer_flag_payload[2];
unsigned int open_cfw_test_onboarding_peer_flag_level_calls;
unsigned int open_cfw_test_onboarding_peer_flag_log_calls;
unsigned int open_cfw_test_onboarding_peer_flag_log_fields[7];
unsigned int open_cfw_test_onboarding_peer_flag_trace_calls;
unsigned int open_cfw_test_onboarding_peer_flag_trace_fields[4];

static void open_cfw_test_onboarding_peer_flag_record(unsigned int event)
{
    open_cfw_test_onboarding_peer_flag_events[
        open_cfw_test_onboarding_peer_flag_event_count++
    ] = event;
}

void open_cfw_test_onboarding_peer_flag_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_peer_flag_value = 0U;
    open_cfw_test_onboarding_peer_flag_send_result = 0;
    open_cfw_test_onboarding_peer_flag_level_value_count = 0U;
    open_cfw_test_onboarding_peer_flag_event_count = 0U;
    open_cfw_test_onboarding_peer_flag_get_calls = 0U;
    open_cfw_test_onboarding_peer_flag_zero_calls = 0U;
    open_cfw_test_onboarding_peer_flag_zero_size = 0U;
    open_cfw_test_onboarding_peer_flag_zero_value = 0U;
    open_cfw_test_onboarding_peer_flag_send_calls = 0U;
    open_cfw_test_onboarding_peer_flag_level_calls = 0U;
    open_cfw_test_onboarding_peer_flag_log_calls = 0U;
    open_cfw_test_onboarding_peer_flag_trace_calls = 0U;
    for (index = 0U; index < 8U; ++index) {
        open_cfw_test_onboarding_peer_flag_level_values[index] = 0U;
    }
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_onboarding_peer_flag_events[index] = 0U;
    }
    for (index = 0U; index < 5U; ++index) {
        open_cfw_test_onboarding_peer_flag_send_fields[index] = 0U;
    }
    for (index = 0U; index < 2U; ++index) {
        open_cfw_test_onboarding_peer_flag_payload[index] = 0U;
    }
    for (index = 0U; index < 7U; ++index) {
        open_cfw_test_onboarding_peer_flag_log_fields[index] = 0U;
    }
    for (index = 0U; index < 4U; ++index) {
        open_cfw_test_onboarding_peer_flag_trace_fields[index] = 0U;
    }
}

static unsigned int open_cfw_test_onboarding_peer_flag_get(void)
{
    open_cfw_test_onboarding_peer_flag_record(1U);
    ++open_cfw_test_onboarding_peer_flag_get_calls;
    return open_cfw_test_onboarding_peer_flag_value;
}

static void *open_cfw_test_onboarding_peer_flag_zero(
    void *buffer,
    unsigned int size,
    unsigned int value
)
{
    open_cfw_test_onboarding_peer_flag_record(2U);
    ++open_cfw_test_onboarding_peer_flag_zero_calls;
    open_cfw_test_onboarding_peer_flag_zero_size = size;
    open_cfw_test_onboarding_peer_flag_zero_value = value;
    memset(buffer, (int)(value & 0xFFU), size);
    return buffer;
}

static int open_cfw_test_onboarding_peer_flag_send(
    unsigned int service,
    const void *payload,
    unsigned int size,
    unsigned int context,
    unsigned int mode
)
{
    const unsigned char *bytes = (const unsigned char *)payload;

    open_cfw_test_onboarding_peer_flag_record(3U);
    ++open_cfw_test_onboarding_peer_flag_send_calls;
    open_cfw_test_onboarding_peer_flag_send_fields[0] = service;
    open_cfw_test_onboarding_peer_flag_send_fields[1] =
        (unsigned int)(uintptr_t)payload;
    open_cfw_test_onboarding_peer_flag_send_fields[2] = size;
    open_cfw_test_onboarding_peer_flag_send_fields[3] = context;
    open_cfw_test_onboarding_peer_flag_send_fields[4] = mode;
    open_cfw_test_onboarding_peer_flag_payload[0] = bytes[0];
    open_cfw_test_onboarding_peer_flag_payload[1] = bytes[1];
    return open_cfw_test_onboarding_peer_flag_send_result;
}

static unsigned int open_cfw_test_onboarding_peer_flag_log_level(void)
{
    unsigned int index = open_cfw_test_onboarding_peer_flag_level_calls++;

    open_cfw_test_onboarding_peer_flag_record(4U);
    if (index >= open_cfw_test_onboarding_peer_flag_level_value_count) {
        return 0U;
    }
    return open_cfw_test_onboarding_peer_flag_level_values[index];
}

static void open_cfw_test_onboarding_peer_flag_log(
    unsigned int level,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *message,
    unsigned int flag
)
{
    open_cfw_test_onboarding_peer_flag_record(5U);
    ++open_cfw_test_onboarding_peer_flag_log_calls;
    open_cfw_test_onboarding_peer_flag_log_fields[0] = level;
    open_cfw_test_onboarding_peer_flag_log_fields[1] =
        (unsigned int)(uintptr_t)module;
    open_cfw_test_onboarding_peer_flag_log_fields[2] =
        (unsigned int)(uintptr_t)file;
    open_cfw_test_onboarding_peer_flag_log_fields[3] =
        (unsigned int)(uintptr_t)function;
    open_cfw_test_onboarding_peer_flag_log_fields[4] = line;
    open_cfw_test_onboarding_peer_flag_log_fields[5] =
        (unsigned int)(uintptr_t)message;
    open_cfw_test_onboarding_peer_flag_log_fields[6] = flag;
}

static void open_cfw_test_onboarding_peer_flag_trace(
    unsigned int level,
    const void *format,
    const void *argument,
    unsigned int flag
)
{
    open_cfw_test_onboarding_peer_flag_record(6U);
    ++open_cfw_test_onboarding_peer_flag_trace_calls;
    open_cfw_test_onboarding_peer_flag_trace_fields[0] = level;
    open_cfw_test_onboarding_peer_flag_trace_fields[1] =
        (unsigned int)(uintptr_t)format;
    open_cfw_test_onboarding_peer_flag_trace_fields[2] =
        (unsigned int)(uintptr_t)argument;
    open_cfw_test_onboarding_peer_flag_trace_fields[3] = flag;
}

#define OPEN_CFW_ONBOARDING_PEER_FLAG_GET() \
    open_cfw_test_onboarding_peer_flag_get()
#define OPEN_CFW_ONBOARDING_PEER_FLAG_ZERO(buffer, size, value) \
    open_cfw_test_onboarding_peer_flag_zero(buffer, size, value)
#define OPEN_CFW_ONBOARDING_PEER_FLAG_SEND(...) \
    open_cfw_test_onboarding_peer_flag_send(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL() \
    open_cfw_test_onboarding_peer_flag_log_level()
#define OPEN_CFW_ONBOARDING_PEER_FLAG_LOG(...) \
    open_cfw_test_onboarding_peer_flag_log(__VA_ARGS__)
#define OPEN_CFW_ONBOARDING_PEER_FLAG_TRACE(...) \
    open_cfw_test_onboarding_peer_flag_trace(__VA_ARGS__)

#include "../../components/apollo_main/core_overlay/onboarding_peer_flag.c"
