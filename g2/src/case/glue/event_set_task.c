/* Export the independently validated CASE event-set body through the public
 * void-pointer ABI while keeping the earlier source and hash unchanged. */
#include "../event-waiters/waiters.c"

uint32_t xEventGroupSetBits(void *event_group_handle, uint32_t flags)
{
    return case_event_set_waiters((event_group *)event_group_handle, flags);
}
