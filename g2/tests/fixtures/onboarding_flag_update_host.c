#include <stdint.h>

unsigned char open_cfw_test_onboarding_flag_update_stored;
unsigned int open_cfw_test_onboarding_flag_update_provider_present;
unsigned int open_cfw_test_onboarding_flag_update_pending;
void *open_cfw_test_onboarding_flag_update_event_handle;
unsigned int open_cfw_test_onboarding_flag_update_set_result;
unsigned int open_cfw_test_onboarding_flag_update_event_result;

unsigned int open_cfw_test_onboarding_flag_update_events[12];
unsigned int open_cfw_test_onboarding_flag_update_event_count;
unsigned int open_cfw_test_onboarding_flag_update_get_calls;
unsigned int open_cfw_test_onboarding_flag_update_get_index;
unsigned int open_cfw_test_onboarding_flag_update_set_calls;
unsigned int open_cfw_test_onboarding_flag_update_set_index;
unsigned int open_cfw_test_onboarding_flag_update_set_value;
unsigned int open_cfw_test_onboarding_flag_update_pending_seen_by_set;
unsigned int open_cfw_test_onboarding_flag_update_event_calls;
unsigned int open_cfw_test_onboarding_flag_update_event_flags;
unsigned int open_cfw_test_onboarding_flag_update_event_handle_seen;
unsigned int open_cfw_test_onboarding_flag_update_pending_seen_by_event;

static void open_cfw_test_onboarding_flag_update_record(unsigned int event)
{
    open_cfw_test_onboarding_flag_update_events[
        open_cfw_test_onboarding_flag_update_event_count++
    ] = event;
}

void open_cfw_test_onboarding_flag_update_reset(void)
{
    unsigned int index;

    open_cfw_test_onboarding_flag_update_stored = 0U;
    open_cfw_test_onboarding_flag_update_provider_present = 1U;
    open_cfw_test_onboarding_flag_update_pending = 0U;
    open_cfw_test_onboarding_flag_update_event_handle =
        (void *)(uintptr_t)0x12345678U;
    open_cfw_test_onboarding_flag_update_set_result = 0U;
    open_cfw_test_onboarding_flag_update_event_result = 0U;
    open_cfw_test_onboarding_flag_update_event_count = 0U;
    open_cfw_test_onboarding_flag_update_get_calls = 0U;
    open_cfw_test_onboarding_flag_update_get_index = 0xFFFFFFFFU;
    open_cfw_test_onboarding_flag_update_set_calls = 0U;
    open_cfw_test_onboarding_flag_update_set_index = 0xFFFFFFFFU;
    open_cfw_test_onboarding_flag_update_set_value = 0U;
    open_cfw_test_onboarding_flag_update_pending_seen_by_set = 0U;
    open_cfw_test_onboarding_flag_update_event_calls = 0U;
    open_cfw_test_onboarding_flag_update_event_flags = 0U;
    open_cfw_test_onboarding_flag_update_event_handle_seen = 0U;
    open_cfw_test_onboarding_flag_update_pending_seen_by_event = 0U;
    for (index = 0U; index < 12U; ++index) {
        open_cfw_test_onboarding_flag_update_events[index] = 0U;
    }
}

static const volatile unsigned char *
open_cfw_test_onboarding_flag_update_get(unsigned int index)
{
    open_cfw_test_onboarding_flag_update_record(1U);
    ++open_cfw_test_onboarding_flag_update_get_calls;
    open_cfw_test_onboarding_flag_update_get_index = index;
    if (open_cfw_test_onboarding_flag_update_provider_present == 0U) {
        return (const volatile unsigned char *)0;
    }
    return &open_cfw_test_onboarding_flag_update_stored;
}

static unsigned int open_cfw_test_onboarding_flag_update_set(
    unsigned int index,
    const unsigned int *value
)
{
    open_cfw_test_onboarding_flag_update_record(2U);
    ++open_cfw_test_onboarding_flag_update_set_calls;
    open_cfw_test_onboarding_flag_update_set_index = index;
    open_cfw_test_onboarding_flag_update_set_value = *value;
    open_cfw_test_onboarding_flag_update_pending_seen_by_set =
        open_cfw_test_onboarding_flag_update_pending;
    open_cfw_test_onboarding_flag_update_stored =
        (unsigned char)(*value & 0xFFU);
    return open_cfw_test_onboarding_flag_update_set_result;
}

static unsigned int open_cfw_test_onboarding_flag_update_event_set(
    void *handle,
    unsigned int flags
)
{
    open_cfw_test_onboarding_flag_update_record(3U);
    ++open_cfw_test_onboarding_flag_update_event_calls;
    open_cfw_test_onboarding_flag_update_event_handle_seen =
        (unsigned int)(uintptr_t)handle;
    open_cfw_test_onboarding_flag_update_event_flags = flags;
    open_cfw_test_onboarding_flag_update_pending_seen_by_event =
        open_cfw_test_onboarding_flag_update_pending;
    return open_cfw_test_onboarding_flag_update_event_result;
}

#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_GET(index) \
    open_cfw_test_onboarding_flag_update_get(index)
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_SET(index, value) \
    open_cfw_test_onboarding_flag_update_set(index, value)
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_PENDING \
    open_cfw_test_onboarding_flag_update_pending
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_HANDLE \
    open_cfw_test_onboarding_flag_update_event_handle
#define OPEN_CFW_ONBOARDING_FLAG_UPDATE_EVENT_SET(handle, flags) \
    open_cfw_test_onboarding_flag_update_event_set(handle, flags)

#include "../../components/apollo_main/core_overlay/onboarding_flag_update.c"
