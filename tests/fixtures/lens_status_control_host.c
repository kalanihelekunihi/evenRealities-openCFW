/*
 * Native host oracle for the bounded lens-status publication helpers.
 */

#include <stdarg.h>
#include <string.h>

unsigned char open_cfw_test_lens_status_state;
unsigned int open_cfw_test_lens_status_available;
unsigned int open_cfw_test_lens_status_selector;
unsigned int open_cfw_test_lens_status_log_levels[4];
unsigned int open_cfw_test_lens_status_log_level_calls;
unsigned int open_cfw_test_lens_status_log_calls;
unsigned int open_cfw_test_lens_status_trace_calls;
unsigned int open_cfw_test_lens_status_template6_calls;
unsigned int open_cfw_test_lens_status_template5_calls;
unsigned int open_cfw_test_lens_status_lens_values[2];
unsigned int open_cfw_test_lens_status_lens_calls;
unsigned int open_cfw_test_lens_status_send_calls;
unsigned int open_cfw_test_lens_status_send_command;
unsigned int open_cfw_test_lens_status_send_size;
unsigned int open_cfw_test_lens_status_send_option;
unsigned char open_cfw_test_lens_status_send_payload[8];

unsigned int open_cfw_test_lens_status_log_severity;
unsigned long open_cfw_test_lens_status_log_module;
unsigned long open_cfw_test_lens_status_log_file;
unsigned long open_cfw_test_lens_status_log_function;
unsigned int open_cfw_test_lens_status_log_line;
unsigned long open_cfw_test_lens_status_log_identity;
unsigned int open_cfw_test_lens_status_trace_event;
unsigned long open_cfw_test_lens_status_trace_identity;

static unsigned int open_cfw_test_lens_status_available_query(void)
{
    return open_cfw_test_lens_status_available;
}

static unsigned int open_cfw_test_lens_status_selector_query(void)
{
    return open_cfw_test_lens_status_selector;
}

static unsigned int open_cfw_test_lens_status_log_level(void)
{
    unsigned int index = open_cfw_test_lens_status_log_level_calls;

    open_cfw_test_lens_status_log_level_calls = index + 1U;
    return open_cfw_test_lens_status_log_levels[index & 3U];
}

static void open_cfw_test_lens_status_log(
    unsigned int severity,
    const void *module,
    const void *file,
    const void *function,
    unsigned int line,
    const void *identity,
    ...
)
{
    open_cfw_test_lens_status_log_calls += 1U;
    open_cfw_test_lens_status_log_severity = severity;
    open_cfw_test_lens_status_log_module = (unsigned long)module;
    open_cfw_test_lens_status_log_file = (unsigned long)file;
    open_cfw_test_lens_status_log_function = (unsigned long)function;
    open_cfw_test_lens_status_log_line = line;
    open_cfw_test_lens_status_log_identity = (unsigned long)identity;
}

static void open_cfw_test_lens_status_trace(
    unsigned int event,
    const void *identity,
    const void *duplicate_identity,
    ...
)
{
    (void)duplicate_identity;
    open_cfw_test_lens_status_trace_calls += 1U;
    open_cfw_test_lens_status_trace_event = event;
    open_cfw_test_lens_status_trace_identity = (unsigned long)identity;
}

static int open_cfw_test_lens_status_send(
    unsigned int command,
    const void *payload,
    unsigned int size,
    unsigned int option
)
{
    open_cfw_test_lens_status_send_calls += 1U;
    open_cfw_test_lens_status_send_command = command;
    open_cfw_test_lens_status_send_size = size;
    open_cfw_test_lens_status_send_option = option;
    memcpy(open_cfw_test_lens_status_send_payload, payload, 8U);
    return -1;
}

unsigned int open_cfw_lens_side(void)
{
    unsigned int index = open_cfw_test_lens_status_lens_calls;

    open_cfw_test_lens_status_lens_calls = index + 1U;
    return open_cfw_test_lens_status_lens_values[index & 1U];
}

unsigned int open_cfw_status_packet_template6(void)
{
    open_cfw_test_lens_status_template6_calls += 1U;
    return 0x00010006U;
}

unsigned int open_cfw_status_packet_template5(void)
{
    open_cfw_test_lens_status_template5_calls += 1U;
    return 0x00010005U;
}

#define OPEN_CFW_LENS_STATUS_STATE open_cfw_test_lens_status_state
#define OPEN_CFW_LENS_STATUS_AVAILABLE() \
    open_cfw_test_lens_status_available_query()
#define OPEN_CFW_LENS_STATUS_SELECTOR() \
    open_cfw_test_lens_status_selector_query()
#define OPEN_CFW_LENS_STATUS_LOG_LEVEL() \
    open_cfw_test_lens_status_log_level()
#define OPEN_CFW_LENS_STATUS_LOG(...) \
    open_cfw_test_lens_status_log(__VA_ARGS__)
#define OPEN_CFW_LENS_STATUS_TRACE(...) \
    open_cfw_test_lens_status_trace(__VA_ARGS__)
#define OPEN_CFW_LENS_STATUS_SEND(command, payload, size, option) \
    open_cfw_test_lens_status_send((command), (payload), (size), (option))
#include "../../components/apollo_main/core_overlay/lens_status_control.c"
