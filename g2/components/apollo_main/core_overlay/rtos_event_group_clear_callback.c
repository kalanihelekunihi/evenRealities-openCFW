/*
 * SPDX-License-Identifier: MIT
 *
 * RTOS event-group clear-bits timer callback matched to stock entry
 * 0x0047EE28.
 */

unsigned int open_cfw_rtos_event_group_clear(
    void *group,
    unsigned int bits_to_clear
);

#ifndef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CALLBACK_CLEAR
#define OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CALLBACK_CLEAR(group, bits) \
    open_cfw_rtos_event_group_clear((group), (bits))
#endif

__attribute__((used, noinline))
void open_cfw_rtos_event_group_clear_callback(
    void *group,
    unsigned int bits_to_clear
)
{
    (void)OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CALLBACK_CLEAR(
        group,
        bits_to_clear
    );
}

#undef OPEN_CFW_RTOS_EVENT_GROUP_CLEAR_CALLBACK_CLEAR
